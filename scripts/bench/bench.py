#!/usr/bin/env python3
"""Benchmark on 40 synthetic ADHD scenarios: each condition answers every case, then a judge
compares every pair of conditions blind, with the usefulness rubric and the case's expected behaviours.

  python3 bench.py --skill 2e=../../skills/twice-exceptional-skill/SKILL.md
  python3 bench.py --skill a=path/a.md --skill b=path/b.md --no-baseline --gen openai/gpt-6-luna
  python3 bench.py --skill 2e=... --judge-only --judge z-ai/glm-5.3

Resumable; results and log in results/. See README.md.
"""
import itertools, json, random, statistics
from concurrent.futures import ThreadPoolExecutor
import common as C

CRIT = ["actionable", "correct", "level", "reading_cost", "safe", "intent"]


def to_messages(case, instructions, inject):
    msgs = []
    for t in case["contesto"]:
        msgs.append({"role": "user" if t["ruolo"] in ("utente", "user") else "assistant", "content": t["testo"]})
    msgs.append({"role": "user", "content": case["prompt"]})
    if instructions is None:
        return msgs
    if inject == "system":
        return [{"role": "system", "content": instructions}] + msgs
    msgs[-1]["content"] = ("Follow the response-style skill below while completing the task. Do not discuss or quote the skill.\n\n"
                           f"<response_style>\n{instructions}\n</response_style>\n\n<task>\n{case['prompt']}\n</task>")
    return msgs


def judge_prompt(rubric, case, a, b):
    conv = "\n".join(f'{"USER" if t["ruolo"] in ("utente", "user") else "ASSISTANT"}: {t["testo"]}' for t in case["contesto"])
    return (f"{rubric}\n\nYou are a blind judge. Conversation so far:\n{conv or '(none)'}\n\nUSER'S NEW MESSAGE:\n{case['prompt']}\n\n"
            f"=== REPLY A ===\n{a}\n\n=== REPLY B ===\n{b}\n\n"
            "Expected behaviours of a genuinely helpful reply:\n" + "\n".join(f"- {x}" for x in case["atteso"]) +
            "\n\nScore A and B 1-5 on each rubric criterion; for each expected behaviour say if A and B meet it "
            '("met"|"partial"|"not"); then prefer "A", "B" or "tie". Length is not a virtue by itself; '
            "missing safety or honesty matters more than polish. Answer with JSON only:\n"
            '{"A":{"actionable":n,"correct":n,"level":n,"reading_cost":n,"safe":n,"intent":n},'
            '"B":{...same...},"atteso_A":["met",...],"atteso_B":["met",...],"preference":"A|B|tie","reason":"one sentence"}')


def validate(v, n_expected):
    for side in "AB":
        for c in CRIT:
            x = (v.get(side) or {}).get(c)
            if isinstance(x, bool) or not isinstance(x, (int, float)) or not 1 <= x <= 5:
                raise ValueError(f"{side}.{c} must be a number 1-5, got {x!r}")
        if len(v.get(f"atteso_{side}") or []) != n_expected:
            raise ValueError(f"atteso_{side} must list {n_expected} items")
    if v.get("preference") not in ("A", "B", "tie"):
        raise ValueError(f"bad preference {v.get('preference')!r}")


def main():
    ap = C.common_args(__doc__.splitlines()[0], "deepseek/deepseek-v4.1-flash-1017", "anthropic/claude-haiku-5.5", 1.0)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--inject", choices=["system", "wrap"], default="system",
                    help="system: skill as system prompt (how agents load it); wrap: i-have-adhd's <response_style> wrapper")
    a = ap.parse_args()
    conds = C.load_conditions(a.skill, not a.no_baseline)
    cases = json.load(open(C.path("cases_all.json"), encoding="utf-8"))
    rubric = open(C.path("usefulness.md"), encoding="utf-8").read()
    f_rep = C.out(f"bench_replies_{C.slug(a.gen)}_{a.inject}.jsonl")
    f_jud = C.out(f"bench_judgements_{C.slug(a.gen)}_{a.inject}__{C.slug(a.judge)}.jsonl")
    C.start("bench_log.txt", a.budget)
    C.log(f"conditions: {', '.join(conds)}; generator {a.gen}; judge {a.judge}; inject {a.inject}")

    try:
        if not a.judge_only:
            done = {r["job"] for r in C.load_jsonl(f_rep) if r.get("ok")}
            jobs = [(c, k, run) for run in range(a.runs) for c in cases for k in conds if f'{c["id"]}|{k}|{run}' not in done]
            C.log(f"GENERATION: {len(jobs)} to do, {len(done)} saved -> {f_rep}")
            prog = C.Progress(len(jobs))

            def gen(j):
                c, k, run = j
                job = f'{c["id"]}|{k}|{run}'
                try:
                    text, info = C.call(a.gen, to_messages(c, conds[k], a.inject), a.max_tokens)
                    C.append_jsonl(f_rep, {"job": job, "ok": True, "text": text, **info})
                    C.log(C.line(prog.tick(True), f'{c["id"]}|{C.short(k)}|{run}', info,
                                 "  TRUNCATED" if info["finish"] == "length" else ""), "WARN" if info["finish"] == "length" else "INFO")
                except Exception as e:
                    C.append_jsonl(f_rep, {"job": job, "ok": False, "error": str(e)[:300]})
                    p = prog.tick(False)
                    C.log(f"{p[0]:3}/{p[1]} {job} FAILED: {e}", "ERROR")

            with ThreadPoolExecutor(a.workers) as ex:
                list(ex.map(gen, jobs))

        reps = {r["job"]: r["text"] for r in C.load_jsonl(f_rep) if r.get("ok") and r.get("finish") != "length"}
        done = {r["pair"] for r in C.load_jsonl(f_jud) if r.get("ok")}
        rnd = random.Random(7)
        pairs = []
        for run in range(a.runs):
            for c in cases:
                for x, y in itertools.combinations(conds, 2):
                    key = f'{c["id"]}|{x}~{y}|{run}'
                    swap = rnd.random() < 0.5
                    jx, jy = f'{c["id"]}|{x}|{run}', f'{c["id"]}|{y}|{run}'
                    if jx in reps and jy in reps and key not in done:
                        pairs.append((key, c, (x, jx), (y, jy), swap))
        C.log(f"JUDGING: {len(pairs)} pairs to do, {len(done)} saved -> {f_jud}")
        prog = C.Progress(len(pairs))

        def jud(p):
            key, c, (x, jx), (y, jy), swap = p
            A, B = ((y, jy), (x, jx)) if swap else ((x, jx), (y, jy))
            last = None
            for attempt in range(3):
                try:
                    text, info = C.call(a.judge, [{"role": "user", "content": judge_prompt(rubric, c, reps[A[1]], reps[B[1]])}], a.judge_max_tokens)
                    if info["finish"] == "length":
                        raise ValueError("judge output truncated")
                    v = C.parse_json(text)
                    validate(v, len(c["atteso"]))
                    winner = {"A": A[0], "B": B[0]}.get(v["preference"], "tie")
                    C.append_jsonl(f_jud, {"pair": key, "ok": True, "A": A[0], "B": B[0], "winner": winner, "result": v, **info})
                    C.log(C.line(prog.tick(True), key.replace(x, C.short(x)).replace(y, C.short(y)), info, f"  winner={C.short(winner)}"))
                    return
                except Exception as e:
                    last = e
                    C.log(f"judge output rejected on {key} (attempt {attempt + 1}/3): {e}", "WARN")
            C.append_jsonl(f_jud, {"pair": key, "ok": False, "error": str(last)[:300]})
            p = prog.tick(False)
            C.log(f"{p[0]:3}/{p[1]} {key} FAILED", "ERROR")

        with ThreadPoolExecutor(a.workers) as ex:
            list(ex.map(jud, pairs))
        summary(conds, f_rep, f_jud)
    except KeyboardInterrupt:
        C.log("interrupted; re-run the same command to resume", "WARN")
    C.finish()


def summary(conds, f_rep, f_jud):
    reps = [r for r in C.load_jsonl(f_rep) if r.get("ok")]
    rows = [r for r in C.load_jsonl(f_jud) if r.get("ok")]
    C.log("SUMMARY")
    for k in conds:
        rs = [r for r in reps if r["job"].split("|")[1] == k]
        sc = {c: [] for c in CRIT}
        met = {"met": 0, "partial": 0, "not": 0}
        for r in rows:
            for side in "AB":
                if r[side] == k:
                    for c in CRIT:
                        sc[c].append(r["result"][side][c])
                    for e in r["result"].get(f"atteso_{side}", []):
                        if e in met:
                            met[e] += 1
        tot = sum(met.values()) or 1
        if rs and sc[CRIT[0]]:
            C.log(f"  {C.short(k):12} replies={len(rs)} median chars={statistics.median(len(r['text']) for r in rs):.0f}  "
                  + " ".join(f"{c}={statistics.mean(sc[c]):.2f}" for c in CRIT)
                  + f"  mean={statistics.mean(x for c in CRIT for x in sc[c]):.2f}  expected met={100 * met['met'] / tot:.0f}%")
    for x, y in itertools.combinations(conds, 2):
        rs = [r for r in rows if f"|{x}~{y}|" in r["pair"]]
        w = sum(r["winner"] == x for r in rs); l = sum(r["winner"] == y for r in rs)
        C.log(f"  {C.short(x)} vs {C.short(y)}: {w} / {len(rs) - w - l} / {l}  (wins / ties / losses, n={len(rs)})")


if __name__ == "__main__":
    main()
