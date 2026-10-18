#!/usr/bin/env python3
"""Check relative links and #anchors in Markdown files, and the SKILL.md frontmatter."""
import re, sys, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
md = [p for p in root.rglob("*.md") if ".git" not in p.parts]
errors = []

def slug(h):
    h = re.sub(r"[`*_]", "", h.strip().lower())
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")

def anchors(p):
    out, seen = set(), {}
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"#{1,6}\s+(.*)", line)
        if m:
            s = slug(m.group(1)); n = seen.get(s, 0); seen[s] = n + 1
            out.add(s if n == 0 else f"{s}-{n}")
    return out

for p in md:
    text = re.sub(r"```.*?```", "", p.read_text(encoding="utf-8"), flags=re.S)
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if re.match(r"[a-z]+:", target):
            continue
        path, _, frag = target.partition("#")
        dest = (p.parent / path).resolve() if path else p
        if not dest.exists():
            errors.append(f"{p.relative_to(root)}: missing {target}")
        elif frag and dest.suffix == ".md" and frag not in anchors(dest):
            errors.append(f"{p.relative_to(root)}: missing anchor {target}")

skill = root / "skills/twice-exceptional-skill/SKILL.md"
fm = re.match(r"---\n(.*?)\n---\n", skill.read_text(encoding="utf-8"), re.S)
if not fm:
    errors.append("SKILL.md: no frontmatter")
else:
    keys = dict(l.split(":", 1) for l in fm.group(1).splitlines() if ":" in l)
    if keys.get("name", "").strip() != skill.parent.name:
        errors.append("SKILL.md: name does not match folder")
    if not keys.get("description", "").strip():
        errors.append("SKILL.md: empty description")

print("\n".join(errors) or f"OK: {len(md)} Markdown files")
sys.exit(1 if errors else 0)
