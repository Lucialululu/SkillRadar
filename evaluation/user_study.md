# SkillRadar — User Study Protocol

## 1. Purpose

We want to evaluate whether SkillRadar is easy to use, whether students find its skill-gap recommendations useful, and whether they trust the results.

## 2. Participants

- Pilot: 2 classmates, approximately 15 minutes each (P01, P02; see `pilot_notes.md`).
- Peer trial: 6–8 job-seeking students who are not in the group, about 20 minutes each (P03 onwards).
- Everyone in the peer trial tests the same app version; the app is not changed between sessions.
- Participation is voluntary.

## 3. Testing Procedure

Step-by-step script for the facilitator: [`peer_trial_guide.md`](peer_trial_guide.md).

We use the think-aloud method. Participants are asked to explain what they are thinking while using SkillRadar. We observe without helping unless necessary.

Each participant completes these tasks:

1. Upload a CV and select a target job role.
2. Review the extracted tools and correct any mistakes.
3. Generate the skill-gap report and explain what it says. For each missing tool shown: "Is it really missing from your CV?" (yes/no; perceived accuracy).
4. Identify one or two tools they would prioritize learning and explain why.

## 4. Consent

Before testing, we tell participants:

"We are testing SkillRadar, not you. Participation is voluntary, and you can stop at any time. We will take anonymous notes about your experience. Your CV will not be included in the report or uploaded to GitHub. You may use a sample CV instead."

We ask for consent before starting. If an external AI service is used to process CV text, we inform participants and request separate consent.

## 5. Questionnaire

After using SkillRadar, participants rate these statements from 1 (strongly disagree) to 5 (strongly agree):

1. SkillRadar correctly identified the tools in my CV.
2. The missing tools seemed relevant to my chosen role.
3. SkillRadar helped me decide what to learn next.
4. I understood why SkillRadar recommended these tools.
5. I trust the information shown in the report.
6. SkillRadar was easy to use.

We also ask:

- What was confusing?
- What would you improve?

## 6. What We Record

For each participant, we record:

- Whether they completed each task without help.
- Any confusion or usability problems.
- Number of tools found, added and removed during confirmation (saved automatically by the app).
- How many of the missing tools shown the participant agrees are really missing.
- Questionnaire ratings (1–5).
- Suggestions for improvement.

Everything is saved by the testing app in step 5: the participant fills in the questionnaire and marks missing tools that are not really missing; the facilitator fills in the task codes and notes in the "For the facilitator" part before saving.

We use anonymous participant IDs (P01, P02, etc.) and do not include personal CV information in the notes.

## 7. Analysis

After the pilot, we identify the main usability problems and improve the app.

After the peer trial, we summarize:

- Task success rates.
- Tool correction rates.
- Perceived accuracy (share of missing tools the participant agrees are missing).
- Questionnaire responses about accuracy, usefulness and trust.
- Recurring usability problems and suggested improvements.

These results will help evaluate Goal 3: whether SkillRadar provides a useful and understandable skill-gap report for students.
