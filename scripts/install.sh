#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
src="$here/skills/twice-exceptional-skill/SKILL.md"
cl="$HOME/.claude"; oc="$HOME/.config/opencode"
imp='@~/.claude/skills/twice-exceptional-skill/SKILL.md'
# shellcheck disable=SC2088  # literal ~, expanded by opencode
ins='~/.claude/skills/twice-exceptional-skill/SKILL.md'

mkdir -p "$cl/skills/twice-exceptional-skill" "$oc/skills/twice-exceptional-skill"
cp "$src" "$cl/skills/twice-exceptional-skill/SKILL.md"
cp "$src" "$oc/skills/twice-exceptional-skill/SKILL.md"

touch "$cl/CLAUDE.md"
grep -qxF "$imp" "$cl/CLAUDE.md" || echo "$imp" >> "$cl/CLAUDE.md"

if [ -f "$oc/opencode.json" ]; then
  cp "$oc/opencode.json" "$oc/opencode.json.bak.$(date +%s)"
  python3 - "$oc/opencode.json" "$ins" <<'PY'
import json, sys
p, f = sys.argv[1:]
d = json.load(open(p))
d.setdefault("instructions", [])
if f not in d["instructions"]:
    d["instructions"].append(f)
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
PY
else
  # shellcheck disable=SC2016  # literal $schema key
  printf '{\n  "$schema": "https://opencode.ai/config.json",\n  "instructions": ["%s"]\n}\n' "$ins" > "$oc/opencode.json"
fi
echo "twice-exceptional-skill installed (Claude Code + opencode)."
