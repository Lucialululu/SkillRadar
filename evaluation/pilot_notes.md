# SkillRadar — Pilot Test Notes

**Purpose:** Find usability problems before the peer trial with 6–8 students, and improve the app between rounds.

**Participants:** 2 classmates outside the group (P01, P02), about 15 minutes each, plus one internal check by a group member (not counted as a participant: they built the app).

**Method:** Think aloud. Participants upload a CV, check/correct the extracted tools, read the skill-gap report, and fill in the in-app questionnaire (step 5). Questionnaire answers are in the study's Google Sheet; this file holds the facilitator's observations and what we changed.

**Privacy:** No names, emails or CV contents here. Consent was asked before each session.

## Overview

| Code | Date | App version | CV | Role (dataset) | Tools found / removed / added |
|---|---|---|---|---|---|
| Internal check | 30 Oct | v1 | own | ML engineer (all) | 12 / 0 / 0 |
| P01 | 31 Oct | v1 | own | software engineer (entry) | 13 / 0 / 0 |
| P02 | 6 Nov | v2 (redesign of 4 Nov) | own | data analyst (entry) | 6 / 0 / 0 |

Nobody removed or added a tool. Either the extraction was right for these CVs, or the check step was skipped. [fill in: did they read the check step, or click through?] → In the peer trial the facilitator notes whether the check step was actually read.

## Ratings (1 = strongly disagree, 5 = strongly agree)

| Statement | Internal | P01 | P02 |
|---|---|---|---|
| Detected tools appeared accurate | 5 | 5 | 5 |
| Missing tools seemed relevant | 5 | 4 | 5 |
| Report helped decide what to learn | 5 | 2 | 3 |
| Understood why tools were recommended | 5 | 4 | 4 |
| Trusted the report | 5 | 5 | 2 |
| App was easy to use | 5 | 5 | 5 |

Ease of use and perceived accuracy are high. **Usefulness (2, 3) and trust (P02: 2) are the weak points**, so these are what the peer trial has to look at.

## Observations per participant

### Internal check (30 Oct, v1)
- Comment: the 95% ranges (confidence intervals) were unclear; wanted more text or labels.
- Suggestion: show the tools you already have above the missing ones, for a more positive first impression.

### P01 (31 Oct, v1)
- Comment: nothing was confusing; found it intuitive.
- Suggestion: the website looks AI-generated.
- Where they hesitated: [fill in, or "not recorded"]

### P02 (6 Nov, v2)
- Comment: somewhat confusing; unsure which jobs they could apply for.
- Suggestion: a short text on how to read the results; make the missing-tools part smaller; say which jobs the CV fits.
- Where they hesitated: [fill in, or "not recorded"]

## What we changed after the pilot

| Problem seen | Change | Version |
|---|---|---|
| 95% ranges unclear | Plain-language key explaining the ranges | v2 (4 Nov) |
| Missing tools shown first felt negative | Report starts with the tools you already have | v2 (4 Nov) |
| Looked generic / AI-made | New look; radar chart of demand; coverage meter | v2 (4 Nov) |
| Unclear what the result means for which jobs | Role overview at the top of the report | v3 (8 Nov) |
| Missing-tools list too long | Shorter missing list | v3 (8 Nov) |
| Report could overstate the match | More careful wording about the match | v3 (8 Nov) |
| No guidance on how to read the report | [fill in: done in v3 or still to do before the trial?] | |

The peer trial (P03 onwards) tests **v3**, frozen for the whole trial.
