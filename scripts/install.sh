#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
src="$here/skills/action-first/SKILL.md"
cl="$HOME/.claude"; oc="$HOME/.config/opencode"
imp='@~/.claude/skills/action-first/SKILL.md'
ins='~/.claude/skills/action-first/SKILL.md'

mkdir -p "$cl/skills/action-first" "$oc/skills/action-first"
cp "$src" "$cl/skills/action-first/SKILL.md"
cp "$src" "$oc/skills/action-first/SKILL.md"

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
  printf '{\n  "$schema": "https://opencode.ai/config.json",\n  "instructions": ["%s"]\n}\n' "$ins" > "$oc/opencode.json"
fi
echo "action-first installed (Claude Code + opencode)."
