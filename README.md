<p align="center">
  <img src="./assets/logo.png" alt="twice-exceptional-skill: a rainbow infinity with a star and lightbulb (gifted) and a lightning bolt with open tabs (ADHD)" width="360" />
</p>
<p align="center">
  <strong>Full expert depth, ADHD-friendly form. Answer first, no filler.</strong>
</p>
<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat" alt="License: MIT"></a>
</p>

Response-style skill for coding agents (Claude Code, opencode): it changes the **form** of the output, not the technical level.

Derived from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) by Ayoub Ghriss (MIT); see [Credits and tooling](#credits-and-tooling).

## What it does

Expert-peer level, with a form that lowers the attention cost of going from "understood" to "done".

| Before | After |
|---|---|
| Context, preamble, "there are several aspects to consider…" | First line = command, path or decision |
| Warning at the bottom | ⚠️ above the steps |
| Long prose | Tables, diagrams, hierarchies |
| Several topics mixed | One thread at a time, switches flagged, 🅿️ parking |
| "Hope this helps!" | No preambles or courtesy closings |
| "You could also try…" after every answer | Extras only for real problems; a finished task ends on "Done: …" |
| Re-answering the same question in new words | After the third time: name what would change the answer, offer to build it |
| Agreeing when the user pushes back | Position changes only for a new fact or argument |

## Install

```bash
git clone https://github.com/JohnnyTriggerDev/twice-exceptional-skill.git
cd twice-exceptional-skill
./scripts/install.sh
```

Idempotent; installs for Claude Code and opencode and loads the skill in every session. Manual steps and verification: [docs/INSTALL.md](docs/INSTALL.md).

## Turn it off

| Scope | How |
|---|---|
| Current session | Write "normal mode" or "stop twice-exceptional-skill" |
| Permanently | Remove the loading lines, see [docs/INSTALL.md#disable](docs/INSTALL.md#disable) |

## Examples (TL;DR)

Five invented prompts, same model, with and without the skill. Full replies side by side: [docs/EXAMPLES.md](docs/EXAMPLES.md).

| Prompt | Without the skill | With the skill | Length |
|---|---|---|---|
| Remove a Docker volume that may be in use | A tutorial with three steps and the caveats at the end | `docker ps -a --filter volume=<name>`, then ⚠️ back up first, **above** the steps | 1,759 → 862 (-51%) |
| SQLite or Postgres for ~100 users? | "Probably SQLite", then four long lists and a question back | **"Use SQLite."**, a ⚠️ with the exception, a table of alternatives | 1,966 → 1,392 (-29%) |
| `i want to add caching to the flask api, redis or in memory,` | A two-option guide with a comparison table | **"Use Redis."**, ⚠️ on the per-worker cache, asks "Plan first or execute?" | 3,502 → 1,591 (-55%) |
| A rough call with the manager, thinking of quitting | Empathy, then a list of questions | Empathy, "no need to decide tonight", **one** question | 832 → 408 (-51%) |
| Move cities to be closer to family? | Three blocks of questions and a regret test | No verdict: the two questions that decide it, offers to draft a message to the family | 1,877 → 812 (-57%) |

Five of eight pairs, picked for readability, one run each: a demo, not a measurement. Without the skill a reply is sometimes the more complete one.

## How it works

Always-on through global instructions, not only when the model picks the skill ([docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)).

```mermaid
flowchart TD
    A[User message] --> B{Deviation applies?}
    B -- "emotional topic / explain / destructive action / ..." --> C[Deviation handling]
    B -- no --> D[First line: answer or action]
    D --> E[⚠️ Warnings]
    E --> F[Numbered steps / table / diagram]
    F --> G[Details under 'Why']
    G --> H[Closing: max 2 blocks]
    H --> I[📌 To remember]
    H --> J[🅿️ Parked]
    H --> K[Last line: Next, or Done when the task is complete]
```

Shape of a response:

```
┌───────────────────────────────┐
│ 1. Answer / next action        │  ← the reader can stop here
├───────────────────────────────┤
│ ⚠️ Warnings and prerequisites  │
├───────────────────────────────┤
│ Steps / table / diagram        │
├───────────────────────────────┤
│ Why / Details                  │
├───────────────────────────────┤
│ 📌 · 🅿️ · Next or Done (max 2) │
└───────────────────────────────┘
```

## Rules at a glance

23 rules in five groups, plus voice mode, closing, 8 deviations and a pre-send check. Map and tables: [docs/RULES.md](docs/RULES.md). Full text: [SKILL.md](skills/twice-exceptional-skill/SKILL.md).

| Group | Rules |
|---|---|
| A. Shape | 1-7: answer first, warnings before steps, expert level, visual structure, one thread, flagged switches, parking |
| B. Doing | 8-12: do don't ask (with a side-effect boundary), plan or execute, immediate goal, failing tools, sensitive data |
| C. Verification | 13: verify before sending, sources visible |
| D. Input | 14-16: fragments, typos, complete dates |
| E. Conversation | 17-23: decisive answers, status, starting and resuming, ready-to-use text, tone, no preambles, language |
| F, G | Voice mode; closing with at most two blocks, "Done: …" or "Done, not run: …" when the task is complete |
| Deviations | Emotional topics, explain, destructive action, debug spiral, question loop, ambiguity, options, environment instructions |

## Limits

- Prompt-only: it shapes how the agent writes, and the model can still drift from it. Nothing in the repo measures compliance.
- System and environment instructions win over the skill (deviation 8); the form stays.
- Not a mental-health tool: on personal and emotional topics the skill steps aside, and it never presents itself as a substitute for a person.

## Evidence

The cited papers document the risks the rules target: sycophancy, dependence on always-available assistants, generic referrals, and lost context after interruptions. No paper tests these rules as prompts, and none tests the question-loop deviation or the "Done" closing directly. Five of the fourteen papers are arXiv preprints. Full table, with each finding, the rule it supports and its limits: [docs/RESEARCH.md](docs/RESEARCH.md).

## Documentation

| File | Content |
|---|---|
| [skills/twice-exceptional-skill/SKILL.md](skills/twice-exceptional-skill/SKILL.md) | The skill (source of truth) |
| [docs/RULES.md](docs/RULES.md) | Map of the 23 rules and the deviations |
| [docs/INSTALL.md](docs/INSTALL.md) | Global install for Claude Code and opencode |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Why a skill plus automatic loading |
| [docs/EXAMPLES.md](docs/EXAMPLES.md) | Five before/after replies, side by side |
| [docs/RESEARCH.md](docs/RESEARCH.md) | Papers, findings, use and limits |

## Credits and tooling

| Source | Use |
|---|---|
| [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd), Ayoub Ghriss, MIT | Original work this skill derives from: core idea and rule-based structure |
| [Kacper Rutkiewicz, AI Made Simple](https://youtu.be/NEl8kPWZP_Y) | Video breakdown of an earlier version of i-have-adhd, cited by the original README |
| [Claude Code memory and `@import`](https://code.claude.com/docs/en/memory) | Automatic loading via `~/.claude/CLAUDE.md` |
| [opencode rules and `instructions`](https://opencode.ai/docs/rules/) | Automatic loading via `opencode.json` |

⚠️ The two documentation links were not re-verified when this README was written; check them if the mechanisms change.

## License

MIT, with the copyright of the original author and of this derivative: see [LICENSE](LICENSE).
