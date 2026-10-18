# OpenRouter benchmarks

Two blind benchmarks that call models through [OpenRouter](https://openrouter.ai) and judge the replies with a model of another family. Standard library only; resumable; logs every call with tokens and cost; hard budget stop. Results: [docs/RESEARCH.md](../../docs/RESEARCH.md#openrouter-benchmarks).

| Script | Cases | Conditions | Judge output |
|---|---|---|---|
| `bench.py` | `cases_all.json`: 40 synthetic ADHD scenarios with expected behaviours, written by an agent that never saw the skill | no skill, version 6, version 7 (via OpenRouter presets `twice-v6` and `twice-v7`, model forced) | pairwise, `usefulness.md` rubric plus the expected behaviours |
| `bench_ihad.py` | `ihad_cases.jsonl`: the 14-case eval suite of [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) (MIT), 3 trials | no skill, this skill (`skills/twice-exceptional-skill/SKILL.md`); optional extra condition from a local `skill_ihad.md` | that suite's rubric block, A/B/C labels and weights, validated like its `parse_judge_scores` |

## Run

```bash
cd scripts/bench
python3 bench.py                      # generate + judge
python3 bench.py judge z-ai/glm-5.3   # re-judge saved replies with another judge
python3 bench_ihad.py run <generator-model> <judge-model>
```

The API key is read at run time from `OPENROUTER_API_KEY`, else from a `.env` next to the scripts, else from opencode's `auth.json`. It is never printed or written. Keep `.env` out of git.

Reasoning models can cost far more than their per-token price suggests: GLM 5.3 used up to 8,800 reasoning tokens per judgement on the 40-case set. Check `bench_log.txt` after the first calls.
