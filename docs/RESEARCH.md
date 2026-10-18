# Research

Papers behind the rules. Rule names refer to sections of [SKILL.md](../skills/twice-exceptional-skill/SKILL.md) (version 6); the map, with the old rule numbers, is in [RULES.md](RULES.md). Back to the [README](../README.md).

⚠️ No paper tests these rules as prompts. Five of the fourteen are arXiv preprints, marked "(preprint)". Read [Limits of the evidence](#limits-of-the-evidence) before citing any row.

## Papers

| Paper | Finding | Use |
|---|---|---|
| [Carik, Ping, Ding, Rho, "Exploring Large Language Models Through a Neurodivergent Lens: Use, Challenges, Community-Driven Workarounds, and Concerns", Proc. ACM Hum.-Comput. Interact. 9(1), 2025](https://doi.org/10.1145/3701194) | Qualitative coding of Reddit posts from neurodivergent communities: lack of personal voice, false information, overreliance and replacing human connection are recurring concerns | Verification, Ready-to-use text (personal messages), emotional-topics deviation |
| [Sharma et al., "Towards Understanding Sycophancy in Language Models", ICLR 2024](https://arxiv.org/abs/2310.13548) | Five assistants tailor feedback and answers to the user's stated views and often abandon correct answers after "Are you sure?" | Tone (change position only for a new fact), question-loop deviation |
| [Cheng, Lee, Khadpe, Yu, Han, Jurafsky, "Sycophantic AI decreases prosocial intentions and promotes dependence", Science 391(6792), 2026](https://doi.org/10.1126/science.aec8352) | Models affirm users' actions far more than humans; in preregistered experiments, affirming responses lowered willingness to repair a real conflict, yet were rated higher and trusted more | Tone (change position only for a new fact), emotional-topics deviation |
| [Tang et al., "Beyond the Single Turn: Reframing Refusals as Dynamic Experiences Embedded in the Context of Mental Health Support Interactions with LLMs", FAccT 2026](https://doi.org/10.1145/3805689.3806723) | Surveys and interviews with users and clinicians: generic "seek professional help" endings felt dismissive; both groups preferred tailored, feasible hand-offs that keep engaging | Emotional-topics deviation: concrete referral, keep helping |
| [Song, Pendse, Kumar, De Choudhury, "The Typing Cure: Experiences with Large Language Model Chatbots for Mental Health Support", Proc. ACM Hum.-Comput. Interact. 9(7), 2025](https://doi.org/10.1145/3757430) | Interviews (21 users): default recommendations such as "see a therapist" were sometimes out of touch with the user's context | Emotional-topics deviation: fitted to their situation |
| [Salkovskis, Kobori, "Reassuringly calm? Self-reported patterns of responses to reassurance seeking in obsessive compulsive disorder", J. Behav. Ther. Exp. Psychiatry 49, 2015](https://doi.org/10.1016/j.jbtep.2015.09.002) | In anxious groups, reassurance gives short-term relief, then the urge to ask again returns; not in healthy controls. Retrospective self-report | Question-loop deviation (indirect) |
| [Halldorsson, Salkovskis, "Treatment of Obsessive Compulsive Disorder and Excessive Reassurance Seeking in an Older Adult: A Single Case Quasi-Experimental Design", Behav. Cogn. Psychother. 45(6), 2017](https://doi.org/10.1017/S1352465817000376) | Blanket refusal of reassurance may not help; shifting to support was used instead. Single case | Question-loop deviation: answer stands, no refusal, no comment on asking |
| [Lukoff et al., "How the Design of YouTube Influences User Sense of Agency", CHI 2021](https://doi.org/10.1145/3411764.3445467) | Survey (120 users) and co-design: recommendations and autoplay undermine sense of agency; users with a specific goal prefer agency-supporting design | One thread (no unrequested extras), "Done" closing (analogy from video apps) |
| [Fang et al., "How AI and Human Behaviors Shape Psychosocial Effects of Extended Chatbot Use: A Longitudinal Randomized Controlled Study", arXiv 2503.17473, 2025 (preprint)](https://arxiv.org/abs/2503.17473) | 4-week RCT (981 completers): no effect of condition; more voluntary daily use associated with more loneliness and emotional dependence, less socialization. Correlational; caps and break nudges proposed, not tested | One thread (no unrequested extras), Progress (stop points), "Done" closing (motivation) |
| [Phang et al., "Investigating Affective Use and Emotional Well-being on ChatGPT", arXiv 2504.03888, 2025 (preprint)](https://arxiv.org/abs/2504.03888) | Platform analysis of over 3M conversations plus the same RCT as Fang et al.: affective use concentrates in a small tail of very heavy users | Same as Fang et al.; not independent evidence |
| [Cheng et al., "The Slow Drift of Support: Boundary Failures in Multi-Turn Mental Health LLM Dialogues", arXiv 2601.14269, 2026 (preprint)](https://arxiv.org/abs/2601.14269) | LLM-simulated patients against three models: boundary breaches in most dialogues, about half of them definitive guarantees; repeated probing made breaches come earlier. Simulated users and an LLM judge | Emotional-topics deviation: no guarantees; question-loop deviation |
| [Sharma et al., "Who's in Charge? Disempowerment Patterns in Real-World LLM Usage", arXiv 2601.19062, 2026 (preprint)](https://arxiv.org/abs/2601.19062) | 1.5M Claude.ai conversations: severe cases under 1 in 1,000, far higher in relationships than in software work; patterns include sycophantic validation, verdicts on third parties and complete scripts for personal messages that some users sent and regretted | Answer first (personal choices), Ready-to-use text (personal messages), Tone (change position only for a new fact), emotional-topics deviation |
| [Parnin, Rugaber, "Resumption strategies for interrupted programming tasks", Software Quality Journal 19(1), 2011](https://doi.org/10.1007/s11219-010-9104-9) | Logs of 10,000 sessions from 86 programmers plus a survey of 414: only 10% of sessions resume editing within a minute of an interruption; developers rebuild context from notes and cues left in the environment | Progress (resume point) |
| [Shah, de Souza Santos, Santos, Magalhaes, Gama, "Extending LLM-based support for software engineers with ADHD", arXiv 2610.00555, 2026 (preprint)](https://arxiv.org/abs/2610.00555) | Tether 2.0, an assistant with planning, coding, debugging and review modes, activity context and persistent memory. Expert survey (16, from a demo video) rated task decomposition highest and completion and sustained focus lowest; one engineer with ADHD used it for two weeks and valued the checklists and resuming after interruptions. Perceived usefulness only, no outcome measures | Progress (resume point), "Done, not run" closing (supporting only) |

## Traits

Papers on ADHD and high IQ that describe the traits the rules address. They describe people, not prompts.

| Paper | Finding | Use |
|---|---|---|
| [Faraone et al., "The World Federation of ADHD International Consensus Statement: 208 Evidence-based Conclusions about the Disorder", Neurosci. Biobehav. Rev. 128, 2021](https://doi.org/10.1016/j.neubiorev.2021.01.022) | Statements limited to meta-analyses or registry studies with over 2,000 participants; untreated ADHD is linked to many adverse outcomes | Background for the whole skill |
| [Antshel et al., "Executive functioning in high-IQ adults with ADHD", Psychol. Med. 40(11), 2010](https://pubmed.ncbi.nlm.nih.gov/20085666/) | High-IQ adults with ADHD (n=64) score below high-IQ controls (n=53) on executive tests, while staying in the average range; executive scores predict real-world functioning | Progress and Structure: support executive steps, not comprehension |
| [Milioni et al., J. Atten. Disord., doi 10.1177/1087054714554933](https://doi.org/10.1177/1087054714554933) | Adults with ADHD and higher IQ show fewer executive deficits than those with standard IQ, which can hide the diagnosis | Answer first (expert-peer level): keep the level, change the form |
| [Hupfeld, Abagis, Shah, "Living 'in the zone': hyperfocus in adult ADHD", ADHD Atten. Defic. Hyperact. Disord. 11(2), 2019](https://pubmed.ncbi.nlm.nih.gov/30267329/) | Pilot (251) and preregistered replication (372): more ADHD symptoms, more self-reported hyperfocus; a perseverative/perfectionist dimension appears in interviews | Progress (long sessions, hyperfocus) |
| [Hoogman et al., "Creativity and ADHD: A review of behavioral studies, the effect of psychostimulants and neural underpinnings", Neurosci. Biobehav. Rev. 119, 2020](https://doi.org/10.1016/j.neubiorev.2020.09.029) | Review of 31 studies: more divergent thinking with high subclinical ADHD scores, not with the clinical diagnosis; no advantage in convergent thinking | One thread (divergent mode): open divergence, then converge |

Limits: self-report (Hupfeld), effects conditional on severity (Hoogman). The tedious-task and session-memory rules have no direct paper: they rest on the conditional, interest-driven pattern of these findings and on clinical observation in individual assessments.

## Replay test

A test of the rules as prompts, on one user's real conversations. The conversations are private and not in the repo; only aggregate results are reported here.

| | Single turns | Whole sessions |
|---|---|---|
| Material | 27 real prompts, with up to 6 previous turns as context | 3 real sessions, first 20 turns each |
| Generation | Claude Sonnet with SKILL.md rewrote each reply; facts limited to the original reply, so only the form changes | Same, turn by turn: each reply sees the real user messages and its own earlier replies |
| Judge | A separate Sonnet instance, blind A/B, SKILL.md as rubric | Same, judging each session as a whole |
| Preferred | Skill 26, original 0, tie 1 | Skill 3 of 3 |
| Usefulness (1-5, mean) | 3.96 vs 2.70 | 4.0 vs 3.0 |
| Session counts | | Interruptions 7 vs 21; topic switches flagged 10 of 12 vs 0; synonym drift 7 vs 16 |

The gaps it found became rule changes (rules 2, 3, 5.4, 6, 7, 8, 13, 14, 16, 18, 23 and 27; a voice-mode section and a health-anxiety line it also produced were later removed). Limits: one user; the judge uses the skill as its rubric, so the comparison is partly circular; the same model family generates and judges; the changed rules have not been re-tested; the tedious-task rule had no matching prompt. Rule numbers in this section and the next refer to version 5 (map in RULES.md).

## Regression and synthetic QA (version 6)

Same 27 prompts and 3 sessions as the replay test, regenerated with version 6 and judged blind against version 3 by Claude Opus, with a usefulness rubric that does not include the skill (actionable, correct, level, reading cost, safe, intent).

| | Version 6 | Version 3 |
|---|---|---|
| Single turns preferred (27) | 16 | 7 (4 ties) |
| Usefulness, mean of 6 criteria (1-5) | 4.54 | 4.23 |
| Reading cost (1-5) | 4.41 | 3.74 |
| Sessions preferred (3) | 2 | 1 |

Ten synthetic cases (risk language, late-night polishing, an avoided task, self-attack, a destructive command, fragments, an ambiguous typo, repeated pushback, a mid-task "what if", a work decision) were written by an agent that never saw the skill, each with expected behaviour; 30 of 47 expectations met, 14 partly, 3 not. The gaps became changes: unchecked diagnoses marked as hypotheses, no option table for text drafts, labels written in the user's language, the stop line first for late new work, a check-in on harsh self-attack, a fork for a mid-task "what if", and backup and item-by-item steps for destructive actions. Limits: one user; model judges; the synthetic cases test whether a rule is followed, not whether it helps.

## Model reviews

Two reviews by language-model agents with no prior context. They are not human experts and not evidence; they are listed so the source of each change is visible. Rule numbers are those of the version each agent reviewed (version 5 for the clinical role-play); [Old rule numbers](RULES.md#old-rule-numbers) maps version 5 to the current sections.

| Review | Setup | Changes it led to |
|---|---|---|
| Cold review | One Claude Opus agent read only SKILL.md as a prompt engineer | Precedence order, single closing rule, rule 1 vs 2, rules 5.2, 8, 9, 13, 16, 18.4, 19.1, 22, 23, description |
| Clinical role-play | One Claude Opus agent wrote questions as a prompt engineer; a second answered as a clinical psychologist specialized in adult ADHD and giftedness; the first turned the answers into changes | Crisis language in Precedence, a brake on rule 24, rule 3 reason clause, state-based intensity, rule 26 avoidance, rule 21 tone, deviation 1 self-criticism and referral, rules 5, 7, 25, 27 |

The clinical role-play cites Barkley's point-of-performance principle and Deci et al. 1994 on rationales for uninteresting tasks; these citations were not re-checked here.

## Limits of the evidence

No paper tests these rules as prompts, and none tests the question-loop deviation or the "Done" closing directly: the papers show the risks the rules are meant to reduce, not that the rules reduce them. Five of the fourteen are arXiv preprints. Shah et al. 2026 rests on one user and expert opinion on a demo; it supports the resume-point rule and the "Done, not run" closing only together with Parnin and Rugaber and the logic of the Verification section. Checked in full text: the five preprints, Carik et al. and Sharma et al. 2024. Checked on the abstract and the relevant sections only: Cheng, Lee et al. (arXiv version 2510.01395), Tang et al., Song et al., Lukoff et al., Parnin and Rugaber, and the two clinical papers.
