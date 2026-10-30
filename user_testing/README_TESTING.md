# SkillRadar user-testing app

`app_testing.py` is the participant version of `app.py`: the same four steps plus a feedback form
(step 5). Feedback is only saved when the participant submits it with consent. It never contains the CV.

## Where feedback is saved

| How the app runs | Feedback goes to |
|---|---|
| Hosted on Streamlit Community Cloud **with** a Google Sheet in its Secrets | the Google Sheet (whole team sees new rows live) |
| On your own computer (`uv run streamlit run app_testing.py`) | `data/user_study/responses.csv` on that computer (gitignored) |

Never rely on the CSV when the app is hosted: Streamlit Cloud wipes its disk on every restart,
sleep and push. Both destinations use the same columns:

`participant_id, test_run, recorded_at_utc, cv_type (sample/own), role, dataset, detected, added, removed,
accuracy, relevance, usefulness, explanation, trust, ease_of_use, main_confusion, suggested_improvement`

The task-success columns (task 1–4: without help / with help / not completed) are observations,
so the facilitator adds them after each session.

## Run locally

```bash
uv sync
uv run streamlit run app_testing.py
```

## 1. Files the hosted app needs

`data/` is ignored except these three, so they can be committed (`git add data/`):

- `data/processed/posting_tools_primary.csv`
- `data/processed/posting_tools_secondary.csv`
- `data/onet/software_skills.csv`

CVs, raw Kaggle data, `data/user_study/` and `.streamlit/secrets.toml` stay ignored.

## 2. Google Sheet (one-time, ~20 min)

1. **Google Cloud project:** go to <https://console.cloud.google.com>, create a project (e.g. `skillradar-study`).
2. **Enable two APIs:** *APIs & Services → Library* → enable **Google Sheets API** and **Google Drive API**.
3. **Service account:** *APIs & Services → Credentials → Create credentials → Service account*,
   name it `skillradar-logger`, skip the optional role steps, click Done.
4. **Key:** open the service account → *Keys → Add key → Create new key → JSON*. A `.json` file downloads.
   Treat it like a password: never commit it, never paste it in chat.
5. **Sheet:** create an empty Google Sheet (e.g. `SkillRadar peer trial`). Click **Share** and add the
   service account's `client_email` (from the JSON, ends in `iam.gserviceaccount.com`) as **Editor**.
6. **Sheet ID:** the long part of the sheet URL between `/d/` and `/edit`.
7. **Secrets:** turn the JSON into this TOML (same values, plus `sheet_id`):

   ```toml
   [gsheets]
   sheet_id = "PASTE_SHEET_ID"
   type = "service_account"
   project_id = "..."
   private_key_id = "..."
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "skillradar-logger@....iam.gserviceaccount.com"
   client_id = "..."
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "..."
   universe_domain = "googleapis.com"
   ```

   Keep `private_key` on one line with the `\n` sequences exactly as in the JSON.
   Optional local test: save it as `.streamlit/secrets.toml` (gitignored) and run the app locally.
   It then writes to the sheet instead of the CSV.

The app writes the header row itself on the first submission. Leave the sheet empty.

## 3. Publish on Streamlit Community Cloud

1. Push everything to `main` (including the three data files, `pyproject.toml` and `uv.lock`).
2. <https://share.streamlit.io> → sign in with GitHub → **Create app** → *Deploy a public app from GitHub*.
3. Repository `Lucialululu/SkillRadar`, branch `main`, main file path **`app_testing.py`**.
   Pick a URL, e.g. `skillradar-study`.
4. **Advanced settings:** Python version **3.14** as in `.python-version` (or the newest one offered); under **Secrets** paste the TOML from step 2.7.
5. **Deploy.** The first build takes a few minutes.
6. Practice run: *Try an example CV* → report → code `TEST01`, tick *Practice submission*, consent, submit.
   A row should appear in the Google Sheet. Delete it before real participants (or filter `test_run = TRUE`).

Secrets can be changed later under the app's *Settings → Secrets*, without a redeploy.

## Notes

- One submission per browser session; the same participant code in a new session is not blocked.
  Give each participant their own code (P01, P02, ...).
- Don't paste participant-level results onto public GitHub. Export a summary for the report.
- If saving fails, the participant sees an error naming the cause type (e.g. `PermissionError`
  usually means the sheet is not shared with the service account).
