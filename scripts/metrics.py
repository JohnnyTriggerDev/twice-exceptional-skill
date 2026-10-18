#!/usr/bin/env python3
"""Success metrics for the skill, computed from a claude.ai data export.

Usage: python3 scripts/metrics.py conversations.json [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--by month|week]

Counts only the user's own messages and prints aggregates: no message text leaves the script.
Patterns cover English and Italian; add your language to PATTERNS.
"""
import argparse, difflib, json, re, statistics, sys
from collections import defaultdict

PATTERNS = {
    # The user asks to change the form of a reply.
    "form_correction": [
        r"\btoo long\b", r"\bshorter\b", r"\bsimpler\b", r"\btl;?dr\b", r"\bin short\b", r"\bkeep it short\b",
        r"\bover-?engineer", r"\boverkill\b", r"\bjust the (answer|command)\b",
        r"\btroppo lung", r"\bpi[uù] (corto|breve|semplice|sintetic)", r"\bsintetizza", r"\bin breve\b",
        r"\bti stai complicando\b", r"\bstai complicando\b", r"\bstai esagerando\b", r"\bsolo (la risposta|il comando)\b",
    ],
    # The user asks what a reply meant: a reading-cost signal.
    "clarification": [
        r"\bwhat do you mean\b", r"\bi don'?t (get|understand)\b", r"^\s*(sorry|wait),? what\b", r"^\s*what are you doing\b",
        r"\bnon ho capito\b", r"\bnon capisco\b", r"\bnon mi [eè] chiaro\b", r"^\s*cio[eè]\b", r"\bche vuol dire\b",
        r"\bin che senso\b", r"^\s*ma (che|perch|come)\b", r"\bscusa\??\s*$", r"^\s*che fai\b",
    ],
    # The user rejects the reply or reports it did not work.
    "pushback": [
        r"^\s*no[ ,.!]", r"\bwrong\b", r"\b(still|again) (broken|failing|not working)\b", r"\bdoesn'?t work\b",
        r"\bsbagliat", r"\bnon (è|era) quello\b", r"\bnon funziona\b", r"\bancora (rotto|errore|non)\b",
    ],
    # The user complains about the form itself, or about feeling constrained by it.
    "form_complaint": [
        r"\btoo many (tables|bullets|emoji)\b", r"\bno (tables|bullets)\b", r"\bstop formatting\b", r"\btoo rigid\b",
        r"\btroppe (tabelle|emoji|liste)\b", r"\bbasta (tabelle|elenchi|emoji)\b", r"\bsenza tabell", r"\btroppo rigid",
        r"\bnormal mode\b", r"\bmodalit[aà] normale\b", r"\bstop 2e\b", r"\bstop twice-exceptional",
    ],
    # The user says outright that the request is being repeated.
    "repeat_marker": [
        r"\bi (already|just) (said|asked|told)\b", r"\bagain\b.*\?", r"\bas i said\b",
        r"\bte l'?ho gi[aà] dett", r"\bl'?ho gi[aà] chiest", r"\bcome ho detto\b", r"\bdi nuovo\b", r"\bripeto\b",
    ],
}
COMPILED = {k: [re.compile(p, re.I) for p in v] for k, v in PATTERNS.items()}
SIMILAR = 0.8   # a user message this similar to one of the previous 3 counts as a repeat
MIN_LEN = 25    # shorter messages ("yes", "go") are not compared


def text_of(m):
    t = m.get("text") or ""
    if not t:
        t = " ".join(c.get("text", "") for c in m.get("content", []) if c.get("type") == "text")
    return t.strip()


def bucket(ts, by):
    return ts[:7] if by == "month" else f"{ts[:4]}-W{__import__('datetime').date.fromisoformat(ts[:10]).isocalendar()[1]:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export")
    ap.add_argument("--since"); ap.add_argument("--until")
    ap.add_argument("--by", choices=["month", "week"], default="month")
    a = ap.parse_args()
    convs = json.load(open(a.export, encoding="utf-8"))

    agg = defaultdict(lambda: defaultdict(int))
    turns = defaultdict(list)
    for c in convs:
        human = [m for m in c.get("chat_messages", []) if m.get("sender") == "human"]
        human = [m for m in human if (not a.since or m["created_at"][:10] >= a.since)
                 and (not a.until or m["created_at"][:10] <= a.until)]
        if not human:
            continue
        b = bucket(human[0]["created_at"], a.by)
        agg[b]["conversations"] += 1
        turns[b].append(len(human))
        prev = []
        for m in human:
            t = text_of(m)
            agg[b]["user_messages"] += 1
            for k, rx in COMPILED.items():
                if any(r.search(t) for r in rx):
                    agg[b][k] += 1
            if len(t) >= MIN_LEN and any(difflib.SequenceMatcher(None, t.lower(), p).ratio() >= SIMILAR for p in prev):
                agg[b]["near_duplicate"] += 1
            prev = (prev + [t.lower()])[-3:] if len(t) >= MIN_LEN else prev

    print("| period | conversations | user msgs | form corrections | clarifications | pushback | repeats | form complaints | median user turns |")
    print("|---|---|---|---|---|---|---|---|---|")
    per = lambda x, n: f"{x} ({100 * x / n:.1f})"
    for b in sorted(agg):
        r = agg[b]; n = r["user_messages"] or 1
        rep = r["repeat_marker"] + r["near_duplicate"]
        print(f"| {b} | {r['conversations']} | {r['user_messages']} | {per(r['form_correction'], n)} | {per(r['clarification'], n)}"
              f" | {per(r['pushback'], n)} | {per(rep, n)} | {per(r['form_complaint'], n)} | {statistics.median(turns[b]):g} |")
    print("\nCounts, with the rate per 100 user messages in brackets.")


if __name__ == "__main__":
    sys.exit(main())
