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
| Warning at the bottom | ⚠️ above the steps, and only for real risks; guesses are labeled "Hypothesis:" |
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
    A[User message] --> P{"Bare preamble ending on a comma?"}
    P -- yes --> P1["Reply only: Yes, go on."]
    P -- no --> B{"Deviation applies?"}
    B -- "emotional topic / explain / destructive action / ..." --> C[Deviation handling]
    B -- no --> D["First line: answer or action"]
    D --> E{"Risk in the steps?"}
    E -- yes --> E1["⚠️ above the steps"]
    E -- no --> F
    E1 --> F["Steps / table / diagram: one representation per concept"]
    F --> G{"Does a Why add new information?"}
    G -- yes --> G1["Why / Details"]
    G -- no --> H
    G1 --> H{"Thread dropped in this message?"}
    H -- yes --> J["🅿️ Parked"]
    H -- no --> I["📌 To remember, only if it changed"]
    J --> K["Last line: Next on the current topic, Done, or Done, not run"]
    I --> K
```

Shape of a response:

```
┌──────────────────────────────────────┐
│ 1. Answer / next action              │  ← the reader can stop here
├──────────────────────────────────────┤
│ ⚠️ Risks, only if there are any      │
├──────────────────────────────────────┤
│ Steps / table / diagram              │
├──────────────────────────────────────┤
│ Why / Details, only if new           │
├──────────────────────────────────────┤
│ 🅿️ or 📌 (optional) · Next or Done   │
└──────────────────────────────────────┘
```

Across a session: "Now:" when the goal changes, "Back to:" when a parked thread resumes, steps named rather than numbered, and the same term for the same concept ([docs/RULES.md](docs/RULES.md#across-a-session)).

## Rules at a glance

27 rules in six groups, plus closing, 8 deviations and a pre-send check. Map and tables: [docs/RULES.md](docs/RULES.md). Full text: [SKILL.md](skills/twice-exceptional-skill/SKILL.md).

| Group | Rules |
|---|---|
| A. Shape | 1-7: answer first, warnings before steps, expert level, visual structure, one thread, flagged switches, parking |
| B. Doing | 8-12: do don't ask (with a side-effect boundary), plan or execute, immediate goal, failing tools, sensitive data |
| C. Verification | 13: verify before sending, sources visible |
| D. Input | 14-16: fragments, typos, complete dates |
| E. Conversation | 17-23: decisive answers, status, starting and resuming, ready-to-use text, tone, no preambles, language |
| F. Closing | Last line Next, Done or "Done, not run"; at most one 🅿️ or 📌 block above it |
| G. Strengths | 24-27: protect hyperfocus, divergent mode, low-interest tasks, repetition |
| Deviations | Emotional topics, explain, destructive action, debug spiral, question loop, ambiguity, options, environment instructions |

## Limits

- Prompt-only: it shapes how the agent writes, and the model can still drift from it. There is no automated compliance check in the repo; one private replay test is summarized in [docs/RESEARCH.md](docs/RESEARCH.md#replay-test).
- System and environment instructions win over the skill (deviation 8); the form stays.
- Not a mental-health tool: on personal and emotional topics the skill steps aside, and it never presents itself as a substitute for a person.

## Evidence

The cited papers document the risks the rules target: sycophancy, dependence on always-available assistants, generic referrals, and lost context after interruptions. No paper tests these rules as prompts, and none tests the question-loop deviation or the "Done" closing directly. Five of the fourteen papers are arXiv preprints. A separate table lists the ADHD and giftedness papers behind the traits that rules 24-27 address. A replay test on one user's real conversations (27 prompts, 3 sessions) preferred the skill in 29 of 30 blind comparisons, with one tie; the judge used the skill as its rubric, so read its limits first. Full tables, with each finding, the rule it supports and its limits: [docs/RESEARCH.md](docs/RESEARCH.md).

## Documentation

| File | Content |
|---|---|
| [skills/twice-exceptional-skill/SKILL.md](skills/twice-exceptional-skill/SKILL.md) | The skill (source of truth) |
| [docs/RULES.md](docs/RULES.md) | Map of the 27 rules and the deviations |
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

Both documentation links checked on 17 October 2026: `@path` imports in `~/.claude/CLAUDE.md` and the `instructions` array in `opencode.json` work as described here.

## License

MIT, with the copyright of the original author and of this derivative: see [LICENSE](LICENSE).
