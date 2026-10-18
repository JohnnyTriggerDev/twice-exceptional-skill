# Installation

Back to the [README](../README.md). How loading works: [ARCHITECTURE.md](ARCHITECTURE.md).

## Automatic

| System | Command |
|---|---|
| Linux, macOS, WSL | `./scripts/install.sh` |
| Windows (PowerShell) | `powershell -ExecutionPolicy Bypass -File scripts\install.ps1` |

Both scripts are tested in CI (run twice, one loading line each). Each script, idempotently:

1. copies the skill to `~/.claude/skills/twice-exceptional-skill/` and `~/.config/opencode/skills/twice-exceptional-skill/`;
2. adds `@~/.claude/skills/twice-exceptional-skill/SKILL.md` to `~/.claude/CLAUDE.md` if missing;
3. adds `~/.claude/skills/twice-exceptional-skill/SKILL.md` to `instructions` in `~/.config/opencode/opencode.json` (backup first).

## Manual

| Tool | Step |
|---|---|
| Claude Code | Copy `skills/twice-exceptional-skill/` to `~/.claude/skills/`; add the line `@~/.claude/skills/twice-exceptional-skill/SKILL.md` to `~/.claude/CLAUDE.md` |
| opencode | Copy to `~/.config/opencode/skills/`; add `~/.claude/skills/twice-exceptional-skill/SKILL.md` (the Claude Code copy, which must exist) to `"instructions"` in `opencode.json` |

## claude.ai and the Claude desktop app

Custom skills need a Pro, Max, Team or Enterprise plan with code execution enabled ([Anthropic help: using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)).

1. Build the ZIP: `cd skills && zip -r twice-exceptional-skill.zip twice-exceptional-skill` (on Windows: right-click the folder, *Send to → Compressed folder*). The folder name must match the `name` in SKILL.md.
2. Settings → Capabilities → Skills → *Upload skill*, and pick the ZIP.
3. A skill loads only when the model picks it. To keep it always on, add to your profile preferences: `Always use the twice-exceptional-skill skill in every reply, on any topic.`

## Verify

Open a new session and ask a short question: the first line must be the answer, with no preamble.

## Disable

Write "normal mode" or "stop twice-exceptional-skill" in chat; to remove it entirely, delete the two loading lines (the `@~/.claude/skills/twice-exceptional-skill/SKILL.md` line in `~/.claude/CLAUDE.md` and the entry in `instructions` in `opencode.json`). The copies under `~/.claude/skills/` and `~/.config/opencode/skills/` can still be invoked as a skill: delete those directories too.
