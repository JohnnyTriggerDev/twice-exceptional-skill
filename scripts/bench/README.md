# OpenRouter benchmarks

Blind benchmarks that call models through [OpenRouter](https://openrouter.ai) and judge the replies with a model of another family. Any skill, several skills, or none: each `--skill NAME=PATH` is one condition, and the no-skill baseline is added unless `--no-baseline`. Python 3.9+, standard library only (Linux, macOS or WSL). Results of the runs so far: [docs/RESEARCH.md](../../docs/RESEARCH.md#openrouter-benchmarks).

| Script | Cases | Judging |
|---|---|---|
| `bench.py` | `cases_all.json`: 40 synthetic ADHD scenarios with expected behaviours, written by an agent that never saw the skill | every pair of conditions, blind, `usefulness.md` rubric plus the expected behaviours |
| `bench_ihad.py` | `ihad_cases.jsonl`: the 14-case eval suite of [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd), 3 trials | all conditions at once under labels A, B, C…, with that suite's rubric block, validation and weights |

## Run

```bash
cd scripts/bench
python3 bench.py --skill 2e=../../skills/twice-exceptional-skill/SKILL.md
python3 bench_ihad.py --skill 2e=../../skills/twice-exceptional-skill/SKILL.md --gen anthropic/claude-haiku-5.5 --judge z-ai/glm-5.3
python3 bench_ihad.py --skill a=path/a.md --skill b=path/b.md --no-baseline      # two skills, no baseline
python3 bench.py --skill 2e=... --judge-only --judge z-ai/glm-5.3                  # re-judge saved replies
python3 bench.py --help
```

| Option | Default |
|---|---|
| `--gen` / `--judge` | `deepseek/deepseek-v4.1-flash-1017` / `anthropic/claude-haiku-5.5` (`bench.py`) or `z-ai/glm-5.3` (`bench_ihad.py`) |
| `--budget` | 1.00 USD (`bench.py`), 0.50 USD (`bench_ihad.py`); the run stops when reached |
| `--inject` (`bench.py`) | `system`: the skill as system prompt, as agents load it; `wrap`: i-have-adhd's `<response_style>` wrapper |
| `--runs` / `--trials` | 1 / 3 |

Every run is resumable: the same command skips what is already saved. A condition is keyed by its name plus a hash of the skill text, so an edited skill never mixes with old replies. Output and logs go to `results/`, which git ignores. Each call is logged with tokens, reasoning tokens, cost, running total and ETA; judge outputs that are malformed or truncated are retried up to three times.

## API key

Read at run time from `OPENROUTER_API_KEY`, else from a `.env` next to the scripts (`OPENROUTER_API_KEY=...`), else from opencode's `~/.local/share/opencode/auth.json`. It is never printed or written. `.env` is in `.gitignore`; never commit it.

Reasoning models can cost far more than their per-token price suggests: GLM 5.3 used up to 8,800 reasoning tokens per judgement on the 40-case set. Watch the first lines of the log.

`ihad_cases.jsonl` and `ihad_rubric_block.md` are copied from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) `evals/`, Copyright (c) 2026 Ayoub Ghriss, MIT License (see [LICENSE](../../LICENSE), which carries that notice).
