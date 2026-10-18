# Evaluations

Reproducible blind comparison of three conditions on the same prompts: **baseline** (no skill), **candidate** (this skill) and **comparator** ([i-have-adhd](https://github.com/ayghri/i-have-adhd), pinned copy in `comparators/`). Back to the [README](../README.md). Latest numbers: [RESULTS.md](RESULTS.md).

| File | Content |
|---|---|
| `cases.jsonl` | 16 single-turn cases: the 10 synthetic cases described in [RESEARCH.md](../docs/RESEARCH.md#regression-and-synthetic-qa-version-6) plus 6 general ones, each with `risk` and `criteria` |
| `scenarios/` | Multi-turn scenario (topic switch, debug spiral, "normal mode"), taken unchanged from i-have-adhd |
| `rubric.md` | Six usefulness dimensions, blocker rule and release gate; the rubric never mentions the skill's rules |
| `comparators/i-have-adhd.SKILL.md` | i-have-adhd at commit `1ecea19` |
| `runners.example.json` | CLI invocation, isolated from the operator's own configuration, model pinned |

## Run

⚠️ Each call is billed to the account the CLI is logged into. With `claude-opus-5-5` a call cost about $0.024 once the prompt cache was warm (the first call of a run pays the cache write, about $0.12). `--budget-usd` caps each generation condition; `judge.py` has no budget flag, so judging (one call per case and trial) is uncapped.

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 3 --include-comparator

for c in baseline candidate comparator; do
  case $c in
    candidate)  s="--condition-skill skills/twice-exceptional-skill/SKILL.md" ;;
    comparator) s="--condition-skill evals/comparators/i-have-adhd.SKILL.md" ;;
    *)          s="" ;;
  esac
  python3 scripts/run_evals.py run --runner claude --condition $c $s \
    --trials 3 --budget-usd 5 --output evals/results/responses.jsonl
done

python3 scripts/judge.py --responses evals/results/responses.jsonl --runner claude \
  --conditions baseline candidate comparator --output evals/results/scores.jsonl
python3 scripts/run_evals.py score evals/results/scores.jsonl
python3 scripts/run_evals.py measure evals/results/responses.jsonl
```

Runs resume: rerun the same command and completed rows are skipped. `evals/results/` is git-ignored; publish the summary in `RESULTS.md` with the model, CLI version, date and cost.

## Limits

- The judge is the same model that generates, and sees all three responses for a case at once. Labels are blind and shuffled per group, but same-family bias is not removed.
- The cases are synthetic and short. They test whether the expected behaviour appears, not whether it helps a real reader over a session; the private replay test in RESEARCH.md covers that, and is not reproducible.
- The candidate skill is long (about 16 KB) and is injected into the user turn, not the system prompt; results may differ when it is loaded through `CLAUDE.md`.

## Credits

`scripts/run_evals.py`, `scripts/judge.py`, `scripts/run_scenario_eval.py`, their tests, `runners.example.json` and the scenario come from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) by Ayoub Ghriss, MIT (`LICENSE.i-have-adhd`). Changes: dimensions read from one `WEIGHTS` table, new rubric and cases, model pin, comparator copy.
