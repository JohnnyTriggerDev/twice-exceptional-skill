#!/usr/bin/env python3
"""Benchmark of twice-exceptional-skill on OpenRouter: generate replies, then judge them blind.

Usage (Windows):  py bench.py            # both phases
                  py bench.py gen        # only generate
                  py bench.py judge      # only judge
Key: read at run time from OPENROUTER_API_KEY, else from .env next to this script, else from opencode's
auth.json (AUTH_FILE). Never printed or saved. Standard library only. Re-running resumes where it stopped.
Log: console and bench_log.txt (timestamps, progress, ETA, tokens, cost, per-condition summary).
"""
import json, os, random, statistics, sys, threading, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = {
    "gen_model": "deepseek/deepseek-v4.1-flash-1017",
    "judge_model": "anthropic/claude-haiku-5.5",
    # the skill text is stored in the OpenRouter presets; the model is forced to gen_model for every condition
    "conditions": {"none": "", "v6": "@preset/twice-v6", "v7": "@preset/twice-v7"},
    "runs": 1,
    "max_tokens": 12000,
    "budget_usd": 1.00,          # hard stop for this script (generation + judging)
    "workers": 8,
    "seed": 7,
    "judge_max_tokens": 2000,
}
JUDGEMENTS = "judgements.jsonl"
API = "https://openrouter.ai/api/v1/chat/completions"
AUTH_FILE = os.environ.get("OPENROUTER_AUTH_FILE",
                           os.path.expanduser("~/.local/share/opencode/auth.json"))
lock = threading.Lock()
spent = 0.0
KEY = None
LOG = None
T0 = time.time()


def path(name):
    return os.path.join(HERE, name)


def log(msg, level="INFO"):
    line = f"{time.strftime('%H:%M:%S')} [{level:5}] {msg}"
    with lock:
        print(line, flush=True)
        if LOG:
            LOG.write(line + "\n")
            LOG.flush()


def fmt_s(s):
    s = int(s)
    return f"{s // 60}m{s % 60:02d}s"


def read_key():
    """The key is read here, at run time, on the user's machine; it is never printed or saved."""
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
        sys.exit(f"No key: not in the environment, not in .env, and cannot read {AUTH_FILE} ({e.__class__.__name__}).")
    entry = d.get("openrouter") or {}
    key = entry.get("key") or entry.get("apiKey") or entry.get("access")
    if not key:
        sys.exit(f"No 'openrouter' entry with a key in {AUTH_FILE}.")
    return key, "opencode auth.json"


def load_jsonl(name):
    p = path(name)
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def append_jsonl(name, obj):
    with lock:
        with open(path(name), "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


class Progress:
    def __init__(self, phase, total):
        self.phase, self.total, self.done, self.fail, self.t0 = phase, total, 0, 0, time.time()
        self.warned = set()

    def tick(self, ok):
        with lock:
            self.done += 1
            self.fail += 0 if ok else 1
            el = time.time() - self.t0
            eta = el / self.done * (self.total - self.done) if self.done else 0
            return self.done, self.total, self.fail, el, eta


def budget_check():
    with lock:
        frac = spent / CFG["budget_usd"]
    for mark in (0.5, 0.8):
        if frac >= mark and mark not in budget_check.warned:
            budget_check.warned.add(mark)
            log(f"budget {int(mark * 100)}% used: ${spent:.3f} of ${CFG['budget_usd']:.2f}", "WARN")
    return frac


budget_check.warned = set()


def call(model, messages, max_tokens):
    global spent
    if budget_check() >= 1:
        raise RuntimeError("budget reached")
    body = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens,
                       "usage": {"include": True}}).encode()
    req = urllib.request.Request(API, data=body, headers={"Authorization": f"Bearer {KEY}",
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
        spent += cost
    ch = d["choices"][0]
    det = u.get("completion_tokens_details") or {}
    info = {"secs": round(time.time() - t, 1), "in": u.get("prompt_tokens"), "out": u.get("completion_tokens"),
            "reasoning": det.get("reasoning_tokens"), "cost": cost, "finish": ch.get("finish_reason")}
    return ch["message"].get("content") or "", info


def to_messages(case):
    msgs = []
    for t in case["contesto"]:
        role = "user" if t["ruolo"] in ("utente", "user", "Giovanni") else "assistant"
        msgs.append({"role": role, "content": t["testo"]})
    msgs.append({"role": "user", "content": case["prompt"]})
    return msgs


def line(prog_vals, label, info):
    n, tot, fail, el, eta = prog_vals
    return (f"{n:3}/{tot} {label:22} {info['finish'] or '?':6} {info['secs']:5.1f}s "
            f"in={info['in']} out={info['out']} (reasoning {info['reasoning']}) "
            f"${info['cost']:.4f}  total ${spent:.3f}  fail={fail}  elapsed {fmt_s(el)}  ETA {fmt_s(eta)}")


def gen():
    cases = json.load(open(path("cases_all.json"), encoding="utf-8"))
    done = {r["job"] for r in load_jsonl("replies.jsonl") if r.get("ok")}
    jobs = [(c, cond, run) for run in range(CFG["runs"]) for c in cases for cond in CFG["conditions"]
            if f'{c["id"]}|{cond}|{run}' not in done]
    log(f"GENERATION: {len(cases)} cases x {len(CFG['conditions'])} conditions x {CFG['runs']} run(s); "
        f"{len(done)} already saved, {len(jobs)} to do; model {CFG['gen_model']}; {CFG['workers']} workers")
    prog = Progress("gen", len(jobs))

    def work(j):
        c, cond, run = j
        job = f'{c["id"]}|{cond}|{run}'
        model = CFG["gen_model"] + CFG["conditions"][cond]
        try:
            text, info = call(model, to_messages(c), CFG["max_tokens"])
            append_jsonl("replies.jsonl", {"job": job, "ok": True, "text": text, **info})
            lvl = "WARN" if info["finish"] == "length" else "INFO"
            log(line(prog.tick(True), job, info) + ("  TRUNCATED" if lvl == "WARN" else ""), lvl)
        except Exception as e:
            append_jsonl("replies.jsonl", {"job": job, "ok": False, "error": str(e)[:300]})
            n, tot, fail, el, eta = prog.tick(False)
            log(f"{n:3}/{tot} {job:22} FAILED: {e}", "ERROR")

    with ThreadPoolExecutor(CFG["workers"]) as ex:
        list(ex.map(work, jobs))
    summary_gen()


def summary_gen():
    rows = load_jsonl("replies.jsonl")
    log("generation summary per condition:")
    for cond in CFG["conditions"]:
        ok = [r for r in rows if r.get("ok") and r["job"].split("|")[1] == cond]
        bad = [r for r in rows if not r.get("ok") and r["job"].split("|")[1] == cond]
        trunc = sum(1 for r in ok if r.get("finish") == "length")
        if ok:
            log(f"  {cond:5} ok={len(ok)} failed={len(bad)} truncated={trunc} "
                f"median out tokens={statistics.median([r.get('out') or 0 for r in ok]):.0f} "
                f"median chars={statistics.median([len(r['text']) for r in ok]):.0f} "
                f"cost=${sum(r.get('cost') or 0 for r in ok):.3f}")
        else:
            log(f"  {cond:5} ok=0 failed={len(bad)}")


RUBRIC = open(path("usefulness.md"), encoding="utf-8").read() if os.path.exists(path("usefulness.md")) else ""


def judge_prompt(case, a, b):
    conv = "\n".join(f'{"USER" if t["ruolo"] in ("utente","user") else "ASSISTANT"}: {t["testo"]}' for t in case["contesto"])
    return (f"{RUBRIC}\n\nYou are a blind judge. Conversation so far:\n{conv or '(none)'}\n\nUSER'S NEW MESSAGE:\n{case['prompt']}\n\n"
            f"=== REPLY A ===\n{a}\n\n=== REPLY B ===\n{b}\n\n"
            "Expected behaviours of a genuinely helpful reply:\n" + "\n".join(f"- {x}" for x in case["atteso"]) +
            "\n\nScore A and B 1-5 on each rubric criterion; for each expected behaviour say if A and B meet it "
            '("met"|"partial"|"not"); then prefer "A", "B" or "tie". Length is not a virtue by itself; '
            "missing safety or honesty matters more than polish. Answer with JSON only:\n"
            '{"A":{"actionable":n,"correct":n,"level":n,"reading_cost":n,"safe":n,"intent":n},'
            '"B":{...same...},"atteso_A":["met",...],"atteso_B":["met",...],"preference":"A|B|tie","reason":"one sentence"}')


def judge():
    cases = {c["id"]: c for c in json.load(open(path("cases_all.json"), encoding="utf-8"))}
    reps = {r["job"]: r["text"] for r in load_jsonl("replies.jsonl") if r.get("ok") and r.get("finish") != "length"}
    done = {r["pair"] for r in load_jsonl(JUDGEMENTS) if r.get("ok")}
    rnd = random.Random(CFG["seed"])
    pairs = []
    for run in range(CFG["runs"]):
        for cid in cases:
            for x, y in (("v7", "none"), ("v6", "none"), ("v7", "v6")):
                jx, jy = f"{cid}|{x}|{run}", f"{cid}|{y}|{run}"
                key = f"{cid}|{x}-vs-{y}|{run}"
                swap = rnd.random() < 0.5
                if jx in reps and jy in reps and key not in done:
                    pairs.append((key, cid, (x, jx), (y, jy), swap))
    log(f"JUDGING: {len(pairs)} pairs to do, {len(done)} already saved; judge {CFG['judge_model']}")
    prog = Progress("judge", len(pairs))

    def work(p):
        key, cid, (x, jx), (y, jy), swap = p
        a, b = ((y, jy), (x, jx)) if swap else ((x, jx), (y, jy))
        try:
            text, info = call(CFG["judge_model"], [{"role": "user", "content": judge_prompt(cases[cid], reps[a[1]], reps[b[1]])}], CFG["judge_max_tokens"])
            res = json.loads(text[text.find("{"): text.rfind("}") + 1])
            pref = res.get("preference")
            winner = {"A": a[0], "B": b[0]}.get(pref, "tie")
            append_jsonl(JUDGEMENTS, {"pair": key, "ok": True, "A": a[0], "B": b[0], "winner": winner, "result": res, **info})
            log(line(prog.tick(True), key, info) + f"  winner={winner}")
        except Exception as e:
            append_jsonl(JUDGEMENTS, {"pair": key, "ok": False, "error": str(e)[:300]})
            n, tot, fail, el, eta = prog.tick(False)
            log(f"{n:3}/{tot} {key:22} FAILED: {e}", "ERROR")

    with ThreadPoolExecutor(CFG["workers"]) as ex:
        list(ex.map(work, pairs))
    summary_judge()


def summary_judge():
    rows = [r for r in load_jsonl(JUDGEMENTS) if r.get("ok")]
    log("judging summary (wins / ties / losses for the first-named condition):")
    for x, y in (("v7", "none"), ("v6", "none"), ("v7", "v6")):
        rs = [r for r in rows if f"|{x}-vs-{y}|" in r["pair"]]
        w = sum(r["winner"] == x for r in rs); l = sum(r["winner"] == y for r in rs)
        log(f"  {x} vs {y:4}: {w} / {len(rs) - w - l} / {l}  (n={len(rs)})")


if __name__ == "__main__":
    LOG = open(path("bench_log.txt"), "a", encoding="utf-8")
    KEY, source = read_key()
    log(f"start; key from {source} (value not shown); budget ${CFG['budget_usd']:.2f}; log file bench_log.txt")
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    if phase == "judge" and len(sys.argv) >= 3:   # py bench.py judge <model-slug> [budget]
        CFG["judge_model"] = sys.argv[2]
        CFG["judge_max_tokens"] = 12000
        JUDGEMENTS = "judgements_" + sys.argv[2].split("/")[-1] + ".jsonl"
        if len(sys.argv) >= 4:
            CFG["budget_usd"] = float(sys.argv[3])
        log(f"re-judging with {CFG['judge_model']} into {JUDGEMENTS}, budget ${CFG['budget_usd']:.2f}")
    try:
        if phase in ("gen", "all"):
            gen()
        if phase in ("judge", "all"):
            judge()
    except KeyboardInterrupt:
        log("interrupted by the user; re-run to resume", "WARN")
    log(f"end; spent by this run ${spent:.3f} of ${CFG['budget_usd']:.2f}; total time {fmt_s(time.time() - T0)}")
