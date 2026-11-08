# SkillRadar peer trial: facilitator guide

Goal 3 test. One session = one participant, about 20 minutes. Protocol and consent text: [`user_study.md`](user_study.md).
Facilitator record: [`peer_trial_results.csv`](peer_trial_results.csv). Questionnaire answers: the Google Sheet (filled in by the participant in step 5 of the app).

## Before the trial (once)

- [ ] **Freeze the app version.** Everyone tests the same version. Note the commit: `git rev-parse --short HEAD` → write it here: `______`. No app changes until the last session is done.
- [ ] **Dry run** the hosted `app_testing.py` with the sample CV, tick "Practice submission", check the row arrives in the Sheet.
- [ ] Recruit **6–8 students who are not in the group** and are job-seeking (internship / first job). Book 20-minute slots (e.g. the 11 Nov peer-testing session).
- [ ] Give each participant a code in order: **P03, P04, …** (P01–P02 were the pilot). Never write names in the repo or the Sheet.
- [ ] Have ready: laptop with the hosted app, the sample CV, this guide, `peer_trial_results.csv` open.

## The session (about 20 min)

### 1. Welcome and consent (2 min), read aloud

> "We are testing SkillRadar, not you. Participation is voluntary and you can stop at any time. We take anonymous notes about how you use it. Your CV is only held in the browser's memory: it is not saved, not put in the report and not uploaded to GitHub. You may use our sample CV instead. At the end you fill in a short questionnaire in the app. Is that OK?"

Only continue with a clear yes. Write `consent = yes` in the CSV.

> "Please think aloud while you work: say what you are looking at, what you expect and what surprises you. I won't help unless you are stuck; that is on purpose."

### 2. Tasks (about 12 min)

Read each task aloud, one at a time. **Do not explain the interface.** If the participant is stuck for ~30 seconds or asks for help, give one small hint and code the task `with_help`.

| # | Read aloud | Done when | CSV column |
|---|---|---|---|
| 1 | "Upload your CV and choose the role you would apply for." | They reach step 3 | `task1_upload_role` |
| 2 | "Check the tools SkillRadar found. Remove any that are wrong and add any it missed." | They continue to the report | `task2_correct_tools` |
| 3 | "Look at the report. Tell me what it says about your CV." Then: **"For each missing tool, is it really missing from your CV? Yes or no."** | They describe coverage/missing tools correctly | `task3_understand_report`, `missing_shown`, `missing_agreed` |
| 4 | "Which one or two tools would you learn first, and why?" | They name a tool and give a reason based on the report | `task4_choose_tool` |

**Codes for the task columns:** `no_help` · `with_help` · `failed`.

For task 3, the "understood" check: can they say in their own words what a percentage means (share of postings for the role) and roughly what the range means (uncertainty)? If they misread it, code `with_help` or `failed` and note how.

**While they work, note (anonymously, no CV content):** where they hesitate, what they misread, what they say out loud. One or two sentences go in `facilitator_notes`.

### 3. Facilitator panel (1 min)

Open **"For the test facilitator"** at the bottom of the report and copy: found → `tools_initial`, removed → `tools_removed`, added → `tools_added`.

Also note whether they actually looked at the check step, or clicked through without reading (`skipped check` in `facilitator_notes`). If everyone skips it, the correction rate says little about Goal 1.

### 4. Questionnaire (3 min)

> "Please fill in step 5. Use the code **P0x**."

Tell them the code; they type it. They answer the six statements and the two questions themselves. **Don't look over their shoulder or comment on ratings.** Check that the green "saved" message appears.

### 5. Close (1 min)

> "Thank you. Is there anything else you want to say about it?"

Add anything new to `facilitator_notes`. If they uploaded their own CV: close the browser tab (it clears the CV from memory).

## After each session (2 min)

- Finish the CSV row while you remember it. One row per participant, same codes every time.
- Don't change the app between sessions. Collect problems in `facilitator_notes`; fix them after the trial.

## After the trial

Export the Google Sheet as CSV (File → Download → CSV) to `data/user_study/sheet_export.csv` (gitignored; it stays off GitHub), then:

```bash
uv run python evaluation/peer_trial_summary.py data/user_study/sheet_export.csv
```

It prints the Goal 3 numbers for the paper: task success per task, correction rate, perceived accuracy, and the questionnaire median and range per statement. Only these summaries go into the report.
