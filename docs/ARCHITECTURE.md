# Architecture

Back to the [README](../README.md). Install steps: [INSTALL.md](INSTALL.md).

A skill alone is invoked only when the model judges it relevant. A style that must apply **always** needs a second channel: global instructions.

```mermaid
flowchart LR
    S[skills/twice-exceptional-skill/SKILL.md]
    S -->|copy| C1[~/.claude/skills/twice-exceptional-skill]
    S -->|copy| O1[~/.config/opencode/skills/twice-exceptional-skill]
    C1 -->|"@import"| C2[~/.claude/CLAUDE.md]
    C1 -->|instructions| O2[opencode.json]
    C2 --> CC[Claude Code: active every session]
    O2 --> OC[opencode: active every session]
```

| Channel | Guarantees start | Role |
|---|---|---|
| Skill | No, the model decides | Availability on invocation |
| `CLAUDE.md` / `instructions` | Yes | Automatic activation |

The file under `skills/` is the single source of truth: re-run `install.sh` after every change to realign the installed copies.
