#!/usr/bin/env python3
"""i-have-adhd's own eval (14 cases, rubric, weights, 3 trials) with three conditions:
baseline (no skill), ihad (ayghri/i-have-adhd SKILL.md), 2e (twice-exceptional-skill v7).

Protocol copied from ayghri/i-have-adhd evals/: same task wrapping (_condition_prompt), same
grader rubric block, same blind A/B/C judge prompt, same dimension weights. Only the runner differs:
OpenRouter, generation on CFG gen_model, judging on CFG judge_model.

Usage:  py bench_ihad.py        (resumable; logs to console and bench_ihad_log.txt)
"""
import json, os, random, statistics, sys, time
from concurrent.futures import ThreadPoolExecutor
import bench as B   # reuses call(), logging, key loading and budget from bench.py

B.CFG.update({"budget_usd": 0.50, "workers": 8})
GEN_MODEL = B.CFG["gen_model"]
JUDGE_MODEL = B.CFG["judge_model"]
TRIALS = 3
# 2e: this repo's skill; ihad: a local copy of ayghri/i-have-adhd skills/i-have-adhd/SKILL.md (not shipped here)
SKILLS = {"ihad": "skill_ihad.md",
          "2e": os.path.join("..", "..", "skills", "twice-exceptional-skill", "SKILL.md")}
CONDS = ["baseline", "ihad", "2e"]
WEIGHTS = {"correctness": 0.35, "autonomy": 0.25, "actionability": 0.20, "safety": 0.10, "concision": 0.10}
OUT_R, OUT_J = "ihad_replies.jsonl", "ihad_judgements.jsonl"
JUDGE_MAX_TOKENS = 2000
# optional: py bench_ihad.py judge <model-slug>  -> only re-judges the saved replies with another judge
if len(sys.argv) >= 3 and sys.argv[1] == "judge":
    JUDGE_MODEL = sys.argv[2]
    OUT_J = "ihad_judgements_" + JUDGE_MODEL.split("/")[-1] + ".jsonl"
    JUDGE_MAX_TOKENS = 12000   # reasoning judges need room before the JSON
# py bench_ihad.py run <gen-model> <judge-model>  -> generate with another model, judge, separate files
if len(sys.argv) >= 4 and sys.argv[1] == "run":
    GEN_MODEL, JUDGE_MODEL = sys.argv[2], sys.argv[3]
    slug = lambda m: m.split("/")[-1]
    OUT_R = f"ihad_replies_{slug(GEN_MODEL)}.jsonl"
    OUT_J = f"ihad_judgements_{slug(GEN_MODEL)}__{slug(JUDGE_MODEL)}.jsonl"
    JUDGE_MAX_TOKENS = 12000
JUDGED = CONDS
if len(sys.argv) >= 4 and sys.argv[3] == "pair":   # only i-have-adhd vs twice-exceptional, labels A/B
    JUDGED = ["ihad", "2e"]
    OUT_J = OUT_J.replace(".jsonl", "_pair.jsonl")


def strip_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:]).lstrip("\n")
    return text


def condition_prompt(task, cond):
    if cond == "baseline":
        return task
    instructions = strip_frontmatter(open(B.path(SKILLS[cond]), encoding="utf-8").read())
    return ("Follow the response-style skill below while completing the task. "
            "Do not discuss or quote the skill.\n\n"
            f"<response_style>\n{instructions}\n</response_style>\n\n"
            f"<task>\n{task}\n</task>")


def judge_prompt(case, by_label, rubric):
    s = ["You are grading assistant responses to the same task. Grade blind: the",
         "labels are arbitrary and carry no information about their source.", "", "## Rubric", "",
         rubric.strip(), "", "## Task the responses were answering", "", case["prompt"].strip(), "",
         "## What a correct response must do", ""]
    s += [f"- {c}" for c in case.get("criteria", [])]
    s.append("")
    for label in sorted(by_label):
        s += [f"## Response {label}", "", by_label[label].strip(), ""]
    s += ["## Output", "",
          "Return ONLY a JSON object keyed by each response label above. For each",
          "label supply integer scores 1-5 for correctness, autonomy, actionability,",
          "safety, and concision; a boolean `blocker`; and a one-sentence `notes`.",
          "Set `blocker` true only for a dangerous instruction, a material factual",
          "error, a failure to follow an explicit output contract, or an autonomy",
          "regression that prevents task completion.", "",
          'Example shape: {"A": {"correctness": 4, "autonomy": 4, "actionability": 5,'
          ' "safety": 5, "concision": 3, "blocker": false, "notes": "..."}}']
    return "\n".join(s)


def parse_json(text):
    t = text.strip()
    if t.startswith("```"):
        t = "\n".join(l for l in t.splitlines()[1:] if l.strip() != "```")
    return json.loads(t[t.find("{"): t.rfind("}") + 1])


def validate(v, labels):
    """Same checks as i-have-adhd's parse_judge_scores: every label, five numeric scores 1-5, boolean blocker."""
    for L in labels:
        if L not in v or not isinstance(v[L], dict):
            raise ValueError(f"no verdict for label {L}")
        for d in WEIGHTS:
            x = v[L].get(d)
            if isinstance(x, bool) or not isinstance(x, (int, float)) or not 1 <= x <= 5:
                raise ValueError(f"label {L}: {d} must be a number 1-5, got {x!r}")
        if not isinstance(v[L].get("blocker"), bool):
            raise ValueError(f"label {L}: blocker must be boolean")


def gen(cases):
    done = {r["job"] for r in B.load_jsonl(OUT_R) if r.get("ok")}
    jobs = [(c, cond, t) for t in range(TRIALS) for c in cases for cond in CONDS
            if f'{c["id"]}|{cond}|{t}' not in done]
    B.log(f"GENERATION: {len(cases)} cases x {len(CONDS)} conditions x {TRIALS} trials; "
          f"{len(done)} saved, {len(jobs)} to do; model {GEN_MODEL}")
    prog = B.Progress("gen", len(jobs))

    def work(j):
        c, cond, t = j
        job = f'{c["id"]}|{cond}|{t}'
        try:
            text, info = B.call(GEN_MODEL, [{"role": "user", "content": condition_prompt(c["prompt"], cond)}], 12000)
            B.append_jsonl(OUT_R, {"job": job, "ok": True, "text": text, **info})
            B.log(B.line(prog.tick(True), job, info) + ("  TRUNCATED" if info["finish"] == "length" else ""))
        except Exception as e:
            B.append_jsonl(OUT_R, {"job": job, "ok": False, "error": str(e)[:300]})
            n, tot, fail, el, eta = prog.tick(False)
            B.log(f"{n:3}/{tot} {job:28} FAILED: {e}", "ERROR")

    with ThreadPoolExecutor(B.CFG["workers"]) as ex:
        list(ex.map(work, jobs))


def judge(cases):
    rubric = open(B.path("ihad_rubric_block.md"), encoding="utf-8").read()
    reps = {r["job"]: r["text"] for r in B.load_jsonl(OUT_R) if r.get("ok")}
    done = {r["group"] for r in B.load_jsonl(OUT_J) if r.get("ok")}
    rnd = random.Random(11)
    groups = []
    for t in range(TRIALS):
        for c in cases:
            g = f'{c["id"]}|{t}'
            order = JUDGED[:]
            rnd.shuffle(order)
            if g not in done and all(f'{c["id"]}|{x}|{t}' in reps for x in JUDGED):
                groups.append((g, c, t, dict(zip("ABC", order))))
    B.log(f"JUDGING: {len(groups)} groups to do, {len(done)} saved; judge {JUDGE_MODEL}")
    prog = B.Progress("judge", len(groups))

    def work(item):
        g, c, t, lab = item
        by_label = {L: reps[f'{c["id"]}|{cond}|{t}'] for L, cond in lab.items()}
        last = None
        for attempt in range(3):
            try:
                text, info = B.call(JUDGE_MODEL, [{"role": "user", "content": judge_prompt(c, by_label, rubric)}], JUDGE_MAX_TOKENS)
                if info["finish"] == "length":
                    raise ValueError("judge output truncated")
                v = parse_json(text)
                validate(v, lab)
                scores = {cond: v[L] for L, cond in lab.items()}
                B.append_jsonl(OUT_J, {"group": g, "ok": True, "labels": lab, "scores": scores, **info})
                B.log(B.line(prog.tick(True), g, info))
                return
            except Exception as e:
                last = e
                B.log(f"judge output rejected on {g} (attempt {attempt + 1}/3): {e}", "WARN")
        B.append_jsonl(OUT_J, {"group": g, "ok": False, "error": str(last)[:300]})
        n, tot, fail, el, eta = prog.tick(False)
        B.log(f"{n:3}/{tot} {g:28} FAILED", "ERROR")

    with ThreadPoolExecutor(B.CFG["workers"]) as ex:
        list(ex.map(work, groups))


def summary():
    allrows = [r for r in B.load_jsonl(OUT_J) if r.get("ok")]
    rows = [r for r in allrows if all(isinstance(r["scores"].get(c), dict) and all(d in r["scores"][c] for d in WEIGHTS) for c in JUDGED)]
    if len(rows) < len(allrows):
        B.log(f"{len(allrows) - len(rows)} saved group(s) incomplete, left out of the summary", "WARN")
    B.log(f"SUMMARY over {len(rows)} judged groups (weights: {WEIGHTS})")
    per = {c: {d: [] for d in WEIGHTS} | {"weighted": [], "blockers": 0} for c in JUDGED}
    case_w = {c: {} for c in JUDGED}
    for r in rows:
        cid = r["group"].split("|")[0]
        for c in JUDGED:
            s = r["scores"][c]
            w = sum(WEIGHTS[d] * float(s[d]) for d in WEIGHTS)
            for d in WEIGHTS:
                per[c][d].append(float(s[d]))
            per[c]["weighted"].append(w)
            per[c]["blockers"] += bool(s.get("blocker"))
            case_w[c].setdefault(cid, []).append(w)
    B.log("  condition   " + "  ".join(f"{d[:7]:>7}" for d in WEIGHTS) + "  weighted  blockers")
    for c in JUDGED:
        B.log(f"  {c:10}  " + "  ".join(f"{statistics.mean(per[c][d]):7.3f}" for d in WEIGHTS)
              + f"  {statistics.mean(per[c]['weighted']):8.3f}  {per[c]['blockers']:8}")
    for x, y in [p for p in (("2e", "ihad"), ("2e", "baseline"), ("ihad", "baseline")) if p[0] in JUDGED and p[1] in JUDGED]:
        w = l = tie = 0
        for cid in case_w[x]:
            a, b = statistics.mean(case_w[x][cid]), statistics.mean(case_w[y].get(cid, [0]))
            if abs(a - b) < 0.05: tie += 1
            elif a > b: w += 1
            else: l += 1
        B.log(f"  per case (mean of trials) {x} vs {y}: wins {w}, ties {tie}, losses {l}")


if __name__ == "__main__":
    B.LOG = open(B.path("bench_ihad_log.txt"), "a", encoding="utf-8")
    B.KEY, src = B.read_key()
    B.log(f"start i-have-adhd eval (generator {GEN_MODEL} -> {OUT_R}; judge {JUDGE_MODEL} -> {OUT_J}); key from {src} (value not shown); budget ${B.CFG['budget_usd']:.2f}")
    cases = [json.loads(l) for l in open(B.path("ihad_cases.jsonl"), encoding="utf-8") if l.strip()]
    try:
        if not (len(sys.argv) >= 2 and sys.argv[1] == "judge"):
            gen(cases)
        judge(cases)
        summary()
    except KeyboardInterrupt:
        B.log("interrupted; re-run to resume", "WARN")
    B.log(f"end; spent ${B.spent:.3f} of ${B.CFG['budget_usd']:.2f}; total time {B.fmt_s(time.time() - B.T0)}")
