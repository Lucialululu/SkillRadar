# SkillRadar peer trial: facilitator guide

Goal 3 test. One session = one participant, about 20 minutes. Protocol and consent text: [`user_study.md`](user_study.md).

**Everything is saved by the app** (`app_testing.py`, step 5) to the Google Sheet: the participant's ratings, comments and which "missing" tools they disagree with, plus the facilitator's task codes and notes. Tool counts (found / removed / added) are saved automatically. You don't keep a separate file.

## Before the trial (once)

- [ ] **Freeze the app version.** Everyone tests the same version. Note the commit: `git rev-parse --short HEAD` → write it here: `______`. No app changes until the last session is done.
- [ ] **Dry run** the hosted `app_testing.py` with the sample CV, tick "Practice submission", fill in the facilitator part too, and check the row arrives in the Sheet with the new columns (`missing_shown` … `facilitator_notes`).
- [ ] Recruit **6–8 students who are not in the group** and are job-seeking (internship / first job). Book 20-minute slots (e.g. the 11 Nov peer-testing session).
- [ ] Give each participant a code in order: **P03, P04, …** (P01–P02 were the pilot). Never write names in the repo or the Sheet.
- [ ] Have ready: laptop with the hosted app, the sample CV, this guide, and paper for short notes while you watch.

## The session (about 20 min)

### 1. Welcome and consent (2 min), read aloud

> "We are testing SkillRadar, not you. Participation is voluntary and you can stop at any time. We take anonymous notes about how you use it. Your CV is only held in the browser's memory: it is not saved, not put in the report and not uploaded to GitHub. You may use our sample CV instead. At the end you fill in a short questionnaire in the app. Is that OK?"

Only continue with a clear yes.

> "Please think aloud while you work: say what you are looking at, what you expect and what surprises you. I won't help unless you are stuck; that is on purpose."

### 2. Tasks (about 12 min)

Read each task aloud, one at a time. **Do not explain the interface.** If the participant is stuck for ~30 seconds or asks for help, give one small hint; that task counts as "With help".

| # | Read aloud | Done when |
|---|---|---|
| 1 | "Upload your CV and choose the role you would apply for." | They reach step 3 |
| 2 | "Check the tools SkillRadar found. Remove any that are wrong and add any it missed." | They continue to the report |
| 3 | "Look at the report. Tell me what it says about your CV." | They describe coverage and the missing tools correctly |
| 4 | "Which one or two tools would you learn first, and why?" | They name a tool and give a reason based on the report |

For task 3, the "understood" check: can they say in their own words what a percentage means (share of postings for the role) and roughly what the range means (uncertainty)? If they misread it: "With help" or "Not completed".

**While they work, jot down on paper (no names, no CV content):** for each task without help / with help / not completed; where they hesitate, what they misread, what they say out loud; whether they actually read the check step or clicked through it.

### 3. Step 5, participant part (3 min)

> "Please fill in step 5 down to the line 'For the facilitator'. Use the code **P0x**."

They type the code, answer the six statements and the two questions, and mark any "missing" tool that is **not** really missing from their CV. **Don't look over their shoulder or comment on ratings.**

### 4. Step 5, facilitator part (2 min)

The participant hands the laptop back. Under **"For the facilitator"**, fill in the four tasks from your paper notes, and one or two sentences in "Where did they hesitate or get stuck?" (add "skipped check step" if they did). Then the participant ticks consent and you press **Save test result**. Check that the green "saved" message appears.

### 5. Close (1 min)

> "Thank you. Is there anything else you want to say about it?"

If it adds something important, it's fine: anything new goes in your notes for the report. Then press **Start over** or close the tab, so the next person starts clean and the CV is gone from memory.

## Between sessions

- Don't change the app between sessions. Collect problems in the notes; fix them after the trial.
- If the app restarts mid-session (e.g. a page reload), let them start again from step 1 and write "restarted" in the notes.
- If a code was typed wrong, fix it in the Sheet afterwards; don't repeat the test.

## After the trial

Export the Google Sheet as CSV (File → Download → CSV) to `data/user_study/sheet_export.csv` (gitignored; it stays off GitHub), then:

```bash
uv run python evaluation/peer_trial_summary.py data/user_study/sheet_export.csv
```

It prints the Goal 3 numbers for the paper: task success per task, correction rate, perceived accuracy, the questionnaire median and range per statement, and the facilitator notes. Only these summaries go into the report.
