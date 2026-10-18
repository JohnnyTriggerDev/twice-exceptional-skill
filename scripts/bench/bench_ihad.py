#!/usr/bin/env python3
"""The 14-case eval suite of ayghri/i-have-adhd, with its task wrapping, rubric block, blind labels,
validation and dimension weights, run on OpenRouter with any set of skills.

  python3 bench_ihad.py --skill 2e=../../skills/twice-exceptional-skill/SKILL.md
  python3 bench_ihad.py --skill a=path/a.md --skill b=path/b.md --no-baseline --gen anthropic/claude-haiku-5.5 --judge z-ai/glm-5.3
  python3 bench_ihad.py --skill 2e=... --judge-only --judge z-ai/glm-5.3

Resumable; results and log in results/. See README.md.
"""
import hashlib, itertools, json, random, statistics, string
from concurrent.futures import ThreadPoolExecutor
import common as C

WEIGHTS = {"correctness": 0.35, "autonomy": 0.25, "actionability": 0.20, "safety": 0.10, "concision": 0.10}


def condition_prompt(task, instructions):
    if instructions is None:
        return task
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


def validate(v, labels):
    """Same checks as i-have-adhd's parse_judge_scores."""
    for L in labels:
        if L not in v or not isinstance(v[L], dict):
            raise ValueError(f"no verdict for label {L}")
        for d in WEIGHTS:
            x = v[L].get(d)
            if isinstance(x, bool) or not isinstance(x, (int, float)) or not 1 <= x <= 5:
                raise ValueError(f"label {L}: {d} must be a number 1-5, got {x!r}")
        if not isinstance(v[L].get("blocker"), bool):
            raise ValueError(f"label {L}: blocker must be boolean")


def weighted(s):
    return sum(WEIGHTS[d] * float(s[d]) for d in WEIGHTS)


def main():
    ap = C.common_args(__doc__.splitlines()[0], "deepseek/deepseek-v4.1-flash-1017", "z-ai/glm-5.3", 0.5)
    ap.add_argument("--trials", type=int, default=3)
    a = ap.parse_args()
    conds = C.load_conditions(a.skill, not a.no_baseline)
    if len(conds) > 26:
        raise SystemExit("at most 26 conditions")
    cases = [json.loads(l) for l in open(C.path("ihad_cases.jsonl"), encoding="utf-8") if l.strip()]
    rubric = open(C.path("ihad_rubric_block.md"), encoding="utf-8").read()
    tag = "+".join(sorted(conds))
    f_rep = C.out(f"ihad_replies_{C.slug(a.gen)}.jsonl")
    f_jud = C.out(f"ihad_judgements_{C.slug(a.gen)}__{C.slug(a.judge)}__{hashlib.sha1(tag.encode()).hexdigest()[:8]}.jsonl")
    C.start("bench_ihad_log.txt", a.budget)
    C.log(f"conditions: {', '.join(conds)}; generator {a.gen}; judge {a.judge}; judgements -> {f_jud}")

    try:
        if not a.judge_only:
            done = {r["job"] for r in C.load_jsonl(f_rep) if r.get("ok")}
            jobs = [(c, k, t) for t in range(a.trials) for c in cases for k in conds if f'{c["id"]}|{k}|{t}' not in done]
            C.log(f"GENERATION: {len(jobs)} to do, {len(done)} saved -> {f_rep}")
            prog = C.Progress(len(jobs))

            def gen(j):
                c, k, t = j
                job = f'{c["id"]}|{k}|{t}'
                try:
                    text, info = C.call(a.gen, [{"role": "user", "content": condition_prompt(c["prompt"], conds[k])}], a.max_tokens)
                    C.append_jsonl(f_rep, {"job": job, "ok": True, "text": text, **info})
                    C.log(C.line(prog.tick(True), f'{c["id"]}|{C.short(k)}|{t}', info, "  TRUNCATED" if info["finish"] == "length" else ""))
                except Exception as e:
                    C.append_jsonl(f_rep, {"job": job, "ok": False, "error": str(e)[:300]})
                    p = prog.tick(False)
                    C.log(f"{p[0]:3}/{p[1]} {job} FAILED: {e}", "ERROR")

            with ThreadPoolExecutor(a.workers) as ex:
                list(ex.map(gen, jobs))

        reps = {r["job"]: r["text"] for r in C.load_jsonl(f_rep) if r.get("ok")}
        done = {r["group"] for r in C.load_jsonl(f_jud) if r.get("ok")}
        rnd = random.Random(11)
        groups = []
        for t in range(a.trials):
            for c in cases:
                g = f'{c["id"]}|{t}'
                order = list(conds)
                rnd.shuffle(order)
                if g not in done and all(f'{c["id"]}|{k}|{t}' in reps for k in conds):
                    groups.append((g, c, t, dict(zip(string.ascii_uppercase, order))))
        C.log(f"JUDGING: {len(groups)} groups to do, {len(done)} saved")
        prog = C.Progress(len(groups))

        def jud(item):
            g, c, t, lab = item
            by_label = {L: reps[f'{c["id"]}|{k}|{t}'] for L, k in lab.items()}
            last = None
            for attempt in range(3):
                try:
                    text, info = C.call(a.judge, [{"role": "user", "content": judge_prompt(c, by_label, rubric)}], a.judge_max_tokens)
                    if info["finish"] == "length":
                        raise ValueError("judge output truncated")
                    v = C.parse_json(text)
                    validate(v, lab)
                    C.append_jsonl(f_jud, {"group": g, "ok": True, "labels": lab, "scores": {k: v[L] for L, k in lab.items()}, **info})
                    C.log(C.line(prog.tick(True), g, info))
                    return
                except Exception as e:
                    last = e
                    C.log(f"judge output rejected on {g} (attempt {attempt + 1}/3): {e}", "WARN")
            C.append_jsonl(f_jud, {"group": g, "ok": False, "error": str(last)[:300]})
            p = prog.tick(False)
            C.log(f"{p[0]:3}/{p[1]} {g} FAILED", "ERROR")

        with ThreadPoolExecutor(a.workers) as ex:
            list(ex.map(jud, groups))
        summary(conds, f_jud)
    except KeyboardInterrupt:
        C.log("interrupted; re-run the same command to resume", "WARN")
    C.finish()


def summary(conds, f_jud):
    rows = [r for r in C.load_jsonl(f_jud) if r.get("ok")
            and all(isinstance(r["scores"].get(k), dict) and all(d in r["scores"][k] for d in WEIGHTS) for k in conds)]
    C.log(f"SUMMARY over {len(rows)} groups (weights {WEIGHTS})")
    C.log("  condition     " + "  ".join(f"{d[:7]:>7}" for d in WEIGHTS) + "  weighted  blockers")
    case_w = {k: {} for k in conds}
    for k in conds:
        sc = [r["scores"][k] for r in rows]
        if not sc:
            continue
        for r in rows:
            case_w[k].setdefault(r["group"].split("|")[0], []).append(weighted(r["scores"][k]))
        C.log(f"  {C.short(k):12}  " + "  ".join(f"{statistics.mean(float(s[d]) for s in sc):7.3f}" for d in WEIGHTS)
              + f"  {statistics.mean(weighted(s) for s in sc):8.3f}  {sum(bool(s['blocker']) for s in sc):8}")
    for x, y in itertools.permutations(conds, 2):
        if list(conds).index(x) < list(conds).index(y):
            continue
        w = l = tie = 0
        for cid in case_w[x]:
            p, q = statistics.mean(case_w[x][cid]), statistics.mean(case_w[y].get(cid, [0]))
            if abs(p - q) < 0.05: tie += 1
            elif p > q: w += 1
            else: l += 1
        C.log(f"  per case (mean of trials) {C.short(x)} vs {C.short(y)}: wins {w}, ties {tie}, losses {l}")


if __name__ == "__main__":
    main()
