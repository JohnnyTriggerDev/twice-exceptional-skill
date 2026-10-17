# twice-exceptional-skill

Response-style skill for coding agents (Claude Code, opencode): it changes the **form** of the output, not the technical level.

Derived from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) (MIT), see [Sources](#sources).

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

## How it works

```mermaid
flowchart TD
    A[User message] --> B{Deviation applies?}
    B -- "emotional topic / explain / destructive action" --> C[Dedicated register, reduced rules]
    B -- no --> D[First line: answer or action]
    D --> E[⚠️ Warnings]
    E --> F[Numbered steps / table / diagram]
    F --> G[Details under 'Why']
    G --> H[Closing: max 2 blocks]
    H --> I[📌 To remember]
    H --> J[🅿️ Parked]
    H --> K[Next: last line]
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
│ 📌 · 🅿️ · Next (max 2)         │
└───────────────────────────────┘
```

## Installation

```bash
git clone https://github.com/tarchia/twice-exceptional-skill.git && cd twice-exceptional-skill
./scripts/install.sh
```

The script is idempotent. Details and manual steps: [docs/INSTALL.md](docs/INSTALL.md).

## Documentation

| File | Content |
|---|---|
| [skills/twice-exceptional-skill/SKILL.md](skills/twice-exceptional-skill/SKILL.md) | The skill (source of truth) |
| [docs/RULES.md](docs/RULES.md) | Map of the 23 rules and the deviations |
| [docs/INSTALL.md](docs/INSTALL.md) | Global install for Claude Code and opencode |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Why a skill plus automatic loading |

## Sources

### Research (papers only)

| Paper | Use |
|---|---|
| [Carik, Ping, Ding, Rho, "Exploring Large Language Models Through a Neurodivergent Lens: Use, Challenges, Community-Driven Workarounds, and Concerns", Proc. ACM Hum.-Comput. Interact. 9(1), 2025](https://arxiv.org/abs/2410.06336) | Neurodivergent users report fear of overreliance and of LLMs replacing human connection: emotional-topics deviation, "Done" closing |
| [Fang et al., "How AI and Human Behaviors Shape Psychosocial Effects of Extended Chatbot Use: A Longitudinal Randomized Controlled Study", arXiv 2503.17473, 2025 (preprint)](https://arxiv.org/abs/2503.17473) | Heavier voluntary use associated with more loneliness, emotional dependence and less socialization: no novelty bait, explicit stop point |
| [Sharma et al., "Towards Understanding Sycophancy in Language Models", arXiv 2310.13548, 2023](https://arxiv.org/abs/2310.13548) | Assistants tend to match the user's views over the correct answer: rule 21.7 |
| [Phang et al., "Investigating Affective Use and Emotional Well-being on ChatGPT", arXiv 2504.03888, 2025 (preprint)](https://arxiv.org/abs/2504.03888) | 3M-conversation analysis, user survey and a 28-day randomized trial: very high usage correlates with more emotional dependence: "Done" closing, explicit stop point |
| [Cheng et al., "The Slow Drift of Support: Boundary Failures in Multi-Turn Mental Health LLM Dialogues", arXiv 2601.14269, 2026 (preprint)](https://arxiv.org/abs/2601.14269) | Safety boundaries erode over long dialogues (definitive guarantees, assuming responsibility, playing professional roles): emotional-topics deviation |
| [Sharma et al., "Who's in Charge? Disempowerment Patterns in Real-World LLM Usage", arXiv 2601.19062, 2026 (preprint)](https://arxiv.org/abs/2601.19062) | 1.5M Claude.ai conversations: rare severe cases, higher in personal domains; sycophantic validation and fully scripted personal communications: rule 21.7, rule 20 caveat |

The question-loop deviation is a design choice: no paper found that tests it directly. Five of the six papers are arXiv preprints; only Carik et al. is a journal paper. They are cited as motivation, not as evidence that these rules reduce harm, and were checked against their abstract or publisher page, not the full text.

### Credits and tooling

| Source | Use |
|---|---|
| [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd), Ayoub Ghriss, MIT | Original work this skill derives from: core idea and rule-based structure |
| [Kacper Rutkiewicz, AI Made Simple](https://youtu.be/NEl8kPWZP_Y) | Video breakdown of an earlier version of i-have-adhd, cited by the original README |
| [Claude Code memory and `@import`](https://code.claude.com/docs/en/memory) | Automatic loading via `~/.claude/CLAUDE.md` |
| [opencode rules and `instructions`](https://opencode.ai/docs/rules/) | Automatic loading via `opencode.json` |

⚠️ The two documentation links were not re-verified when this README was written; check them if the mechanisms change.

## License

MIT, with the copyright of the original author and of this derivative: see [LICENSE](LICENSE).
