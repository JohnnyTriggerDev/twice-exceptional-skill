# Installation

Back to the [README](../README.md). How loading works: [ARCHITECTURE.md](ARCHITECTURE.md).

## Automatic

```bash
./scripts/install.sh
```

The script, idempotently:

1. copies the skill to `~/.claude/skills/twice-exceptional-skill/` and `~/.config/opencode/skills/twice-exceptional-skill/`;
2. adds `@~/.claude/skills/twice-exceptional-skill/SKILL.md` to `~/.claude/CLAUDE.md` if missing;
3. adds `~/.claude/skills/twice-exceptional-skill/SKILL.md` to `instructions` in `~/.config/opencode/opencode.json` (backup first).

## Manual

| Tool | Step |
|---|---|
| Claude Code | Copy `skills/twice-exceptional-skill/` to `~/.claude/skills/`; add the line `@~/.claude/skills/twice-exceptional-skill/SKILL.md` to `~/.claude/CLAUDE.md` |
| opencode | Copy to `~/.config/opencode/skills/`; add the path to `"instructions"` in `opencode.json` |

## Verify

Open a new session and ask a short question: the first line must be the answer, with no preamble.

## Disable

Write "normal mode" or "stop twice-exceptional-skill" in chat; to remove it entirely, delete the two loading lines (the `@~/.claude/skills/twice-exceptional-skill/SKILL.md` line in `~/.claude/CLAUDE.md` and the entry in `instructions` in `opencode.json`). The copies under `~/.claude/skills/` and `~/.config/opencode/skills/` can still be invoked as a skill: delete those directories too.
