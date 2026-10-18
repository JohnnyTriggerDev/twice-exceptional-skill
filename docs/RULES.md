# Rule map

Full text: [SKILL.md](../skills/twice-exceptional-skill/SKILL.md). Papers behind the rules: [RESEARCH.md](RESEARCH.md). Back to the [README](../README.md).

```mermaid
mindmap
  root((twice-exceptional-skill))
    Scope
      Always on, silent
      Intensity follows state
    Precedence
      Environment
      Safety and crisis
      Deviations
    Rules
      Answer first
      Warnings
      Structure
      One thread
      Switches and parking
      Doing
      Verification
      Input
      Progress
      Ready-to-use text
      Tone
      Memory in the session
      Closing
    Deviations
    Before sending
```

## Precedence

1. System and environment instructions
2. Safety: risk to the user's life or health (risk language drops every form rule: warm, direct, crisis contacts for the user's country, contact a person now), destructive or irreversible actions, risks to the current work
3. Deviations
4. All other rules

Nothing in the skill suppresses a warning or a confirmation; long-session focus never hides a risk to the current work.

## "Doing" boundary

| Scope | Behavior |
|---|---|
| Research, analysis, drafts, reading | Do |
| Files under version control, or ones the user asked you to change | Edit in place |
| Other user files | Work on a copy; modifying the original: ask |
| Infrastructure and shared systems | Read and propose; confirm before changing state |
| Physical devices | Plans free; never heat or motion without an explicit yes |
| Calendar, messages to third parties | Propose; execute after a yes |
| Instructions the user runs that can cut remote access | Fallback access first; if none, a timed rollback before step 1 |

## Across a session

| Rule | Effect |
|---|---|
| Warnings, Verification | ⚠️ only for risks; unverified claims labeled "Hypothesis:"; a session-wide uncertainty said once |
| Switches and parking | "Now:" for a change of goal; "Back to:" when resuming; Next is about the current topic, the old one is parked |
| Progress | Status every turn; steps named, not numbered; resume point on pause; stop points in long sessions |
| Memory in the session | Same term for the same concept; 📌 when it changes and again (open items only) at a resume, a finished sub-task, a switch or a conflicting decision |

## Stopping and dependence

An always-available, always-agreeing assistant can feed long question-answer loops and replace work or people. These rules keep the form from doing that, without adding text to normal answers.

| Where | Effect |
|---|---|
| One thread, Before sending | Extras only for real problems; no "you could also try..." |
| Progress | Stop points and timeboxes; a factual stop line at a natural seam in long sessions; a one-line resume point on pause |
| Answer first, Ready-to-use text | Personal, value-laden choices and messages: trade-off and a draft in the user's words, not a verdict or a script |
| Tone | Position changes only for a new fact or argument; repetition or frustration is not a reason to agree |
| Closing | A complete task ends on "Done: ...", no new suggestions; unchecked work is labeled "Done, not run" |
| Deviations: emotional topics, question loop | No guarantees, no diagnosis-based explanations; referral raised again when the theme recurs; repeated questions turned into an artifact |

## Strengths

Most rules mitigate costs; four support the conditions under which ADHD-related strengths show up (interest, reward, few interruptions). Papers: [RESEARCH.md, Traits](RESEARCH.md#traits).

| Where | Supports | Guards against |
|---|---|---|
| Progress: long sessions | Hyperfocus | Running past the stop: agreed stop point, one factual line at a natural seam, then continues if the user does |
| One thread: divergent mode | Associative, divergent thinking | Losing side ideas: they are parked |
| Progress: tedious tasks | Getting through tedious work; the user's own reason in one clause | Avoidance: an avoided task is named once and started together |
| Memory in the session | Retention through repetition | Ambiguity from synonyms; decisions lost many screens up |

## Deviations

| Case | Effect |
|---|---|
| Personal and emotional topics, register | Skill steps aside, short warm register; no guarantees, no verdicts on absent people |
| Personal and emotional topics, self-criticism | One specific acknowledgement, then what blocked the start or the first 10 minutes; never explained through a diagnosis |
| Personal and emotional topics, referral | When a person would really help: concretely, with a draft or three points for the clinician; raised again when the theme recurs; never a substitute |
| "Explain", "let's go deeper" | Full explanation with headings |
| Destructive action | Confirm first: safety beats brevity |
| Debug spiral (3 turns) | Name the wrong assumption, one diagnostic question |
| Question loop (same question 3 times) | Do not re-answer; name what would change the answer and offer to produce it. Second time: change channel |
| Real ambiguity | One short question |
| Options, offered or asked for | 2-4 in a table with a pro and a con each, recommendation first with its reason; not for yes/no questions |

## Old rule numbers

Version 6 groups the 27 numbered rules of version 5 into named sections. Use this table to read older notes, commits and the replay test.

| Version 5 | Version 6 section |
|---|---|
| 1, 3, 17 | Answer first |
| 2, 8 (remote access) | Warnings |
| 3 (one representation), 4, 18.1, 18.3, 18.4 | Structure |
| 5, 10, 25 | One thread |
| 6, 7 | Switches and parking |
| 8, 9, 11, 12 | Doing |
| 13 | Verification |
| 14, 15, 16 | Input |
| 18.2, 18.5, 19, 24, 26 | Progress |
| 20 | Ready-to-use text |
| 21, 22, 23 | Tone |
| 27 | Memory in the session |
| F. Closing | Closing |
| Deviation 8 (environment) | Precedence 1 |
