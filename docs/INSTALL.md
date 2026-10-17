# Installation

## Automatic

```bash
./scripts/install.sh
```

The script, idempotently:

1. copies the skill to `~/.claude/skills/action-first/` and `~/.config/opencode/skills/action-first/`;
2. adds `@~/.claude/skills/action-first/SKILL.md` to `~/.claude/CLAUDE.md` if missing;
3. adds `~/.claude/skills/action-first/SKILL.md` to `instructions` in `~/.config/opencode/opencode.json` (backup first).

## Manual

| Tool | Step |
|---|---|
| Claude Code | Copy `skills/action-first/` to `~/.claude/skills/`; add the line `@~/.claude/skills/action-first/SKILL.md` to `~/.claude/CLAUDE.md` |
| opencode | Copy to `~/.config/opencode/skills/`; add the path to `"instructions"` in `opencode.json` |

## Verify

Open a new session and ask a short question: the first line must be the answer, with no preamble.

## Disable

Write "normal mode" or "stop action-first" in chat; to remove it entirely, delete the two loading lines.
