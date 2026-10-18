"""Shared plumbing for the OpenRouter benchmarks: key, calls, budget, logging, files, skills.

Standard library only. The API key is read at run time from OPENROUTER_API_KEY, else from a .env
next to these scripts, else from opencode's auth.json; it is never printed or written anywhere.
"""
import argparse, hashlib, json, os, sys, threading, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
API = "https://openrouter.ai/api/v1/chat/completions"
AUTH_FILE = os.environ.get("OPENROUTER_AUTH_FILE", os.path.expanduser("~/.local/share/opencode/auth.json"))

lock = threading.Lock()
state = {"spent": 0.0, "budget": 1.0, "key": None, "log": None, "t0": time.time(), "warned": set()}


# ---------- files and logging ----------

def path(name):
    return os.path.join(HERE, name)


def out(name):
    os.makedirs(RESULTS, exist_ok=True)
    return os.path.join(RESULTS, name)


def slug(model):
    return model.split("/")[-1].replace(":", "_")


def log(msg, level="INFO"):
    line = f"{time.strftime('%H:%M:%S')} [{level:5}] {msg}"
    with lock:
        print(line, flush=True)
        if state["log"]:
            state["log"].write(line + "\n")
            state["log"].flush()


def fmt_s(s):
    s = int(s)
    return f"{s // 60}m{s % 60:02d}s"


def load_jsonl(p):
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def append_jsonl(p, obj):
    with lock:
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


# ---------- skills and conditions ----------

def strip_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:]).lstrip("\n")
    return text


def load_conditions(skill_args, baseline=True):
    """--skill NAME=PATH (repeatable) -> {condition: instructions or None}. The condition key carries
    a short hash of the skill text, so editing a skill file never mixes old and new replies."""
    conds = {"baseline": None} if baseline else {}
    for arg in skill_args or []:
        name, sep, p = arg.partition("=")
        if not sep or not name or not p:
            sys.exit(f"--skill expects NAME=PATH, got {arg!r}")
        if name == "baseline" or "|" in name or "@" in name:
            sys.exit(f"invalid skill name {name!r}")
        p = os.path.expanduser(p)
        if not os.path.isabs(p):
            p = os.path.join(os.getcwd(), p)
        if not os.path.exists(p):
            sys.exit(f"skill file not found: {p}")
        text = strip_frontmatter(open(p, encoding="utf-8").read())
        conds[f"{name}@{hashlib.sha1(text.encode()).hexdigest()[:8]}"] = text
    if len(conds) < 2:
        sys.exit("need at least two conditions: baseline plus one --skill, or two --skill with --no-baseline")
    return conds


def short(cond):
    return cond.split("@")[0]


def common_args(desc, default_gen, default_judge, default_budget):
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("--skill", action="append", metavar="NAME=PATH",
                    help="a skill to test; repeat for several (e.g. --skill 2e=../../skills/twice-exceptional-skill/SKILL.md)")
    ap.add_argument("--no-baseline", action="store_true", help="leave out the no-skill condition")
    ap.add_argument("--gen", default=default_gen, help=f"model that answers (default {default_gen})")
    ap.add_argument("--judge", default=default_judge, help=f"model that judges (default {default_judge})")
    ap.add_argument("--judge-only", action="store_true", help="only judge replies already saved")
    ap.add_argument("--budget", type=float, default=default_budget, help=f"hard stop in USD (default {default_budget})")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=12000)
    ap.add_argument("--judge-max-tokens", type=int, default=12000, help="reasoning judges need room before the JSON")
    return ap


def start(logname, budget):
    state["budget"] = budget
    state["log"] = open(out(logname), "a", encoding="utf-8")
    state["key"], src = read_key()
    log(f"key from {src} (value not shown); budget ${budget:.2f}; results in {RESULTS}")


# ---------- key and API ----------

def read_key():
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"], "environment variable"
    env = path(".env")
    if os.path.exists(env):
        for line in open(env, encoding="utf-8-sig"):
            k, _, v = line.strip().partition("=")
            if k.strip().removeprefix("export ").strip() == "OPENROUTER_API_KEY" and v.strip():
                return v.strip().strip('"').strip("'"), ".env"
    try:
        d = json.load(open(AUTH_FILE, encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"No key: set OPENROUTER_API_KEY, or put it in {env}, or log in to OpenRouter in opencode ({e.__class__.__name__}).")
    entry = d.get("openrouter") or {}
    key = entry.get("key") or entry.get("apiKey") or entry.get("access")
    if not key:
        sys.exit(f"No 'openrouter' entry with a key in {AUTH_FILE}.")
    return key, "opencode auth.json"


def budget_check():
    with lock:
        frac = state["spent"] / state["budget"]
    for mark in (0.5, 0.8):
        if frac >= mark and mark not in state["warned"]:
            state["warned"].add(mark)
            log(f"budget {int(mark * 100)}% used: ${state['spent']:.3f} of ${state['budget']:.2f}", "WARN")
    return frac


def call(model, messages, max_tokens):
    if budget_check() >= 1:
        raise RuntimeError("budget reached")
    body = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens,
                       "usage": {"include": True}}).encode()
    req = urllib.request.Request(API, data=body, headers={"Authorization": f"Bearer {state['key']}",
                                                         "Content-Type": "application/json"})
    t = time.time()
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.load(r)
            break
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:200]
            log(f"HTTP {e.code} on {model} (attempt {attempt + 1}/3): {detail}", "WARN")
            if attempt == 2 or e.code in (400, 401, 402, 403):
                raise RuntimeError(f"HTTP {e.code}: {detail}")
            time.sleep(5 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError) as e:
            log(f"network error on {model} (attempt {attempt + 1}/3): {e}", "WARN")
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))
    if "error" in d:
        raise RuntimeError(f"API error: {str(d['error'])[:200]}")
    u = d.get("usage", {})
    cost = float(u.get("cost") or 0)
    with lock:
        state["spent"] += cost
    ch = d["choices"][0]
    det = u.get("completion_tokens_details") or {}
    info = {"secs": round(time.time() - t, 1), "in": u.get("prompt_tokens"), "out": u.get("completion_tokens"),
            "reasoning": det.get("reasoning_tokens"), "cost": cost, "finish": ch.get("finish_reason")}
    return ch["message"].get("content") or "", info


def parse_json(text):
    t = text.strip()
    if t.startswith("```"):
        t = "\n".join(l for l in t.splitlines()[1:] if l.strip() != "```")
    return json.loads(t[t.find("{"): t.rfind("}") + 1])


# ---------- progress ----------

class Progress:
    def __init__(self, total):
        self.total, self.done, self.fail, self.t0 = total, 0, 0, time.time()

    def tick(self, ok):
        with lock:
            self.done += 1
            self.fail += 0 if ok else 1
            el = time.time() - self.t0
            eta = el / self.done * (self.total - self.done) if self.done else 0
            return self.done, self.total, self.fail, el, eta


def line(p, label, info, extra=""):
    n, tot, fail, el, eta = p
    return (f"{n:3}/{tot} {label:32} {info['finish'] or '?':6} {info['secs']:5.1f}s in={info['in']} out={info['out']} "
            f"(reasoning {info['reasoning']}) ${info['cost']:.4f}  total ${state['spent']:.3f}  fail={fail}  "
            f"elapsed {fmt_s(el)}  ETA {fmt_s(eta)}{extra}")


def finish():
    log(f"end; spent ${state['spent']:.3f} of ${state['budget']:.2f}; total time {fmt_s(time.time() - state['t0'])}")
