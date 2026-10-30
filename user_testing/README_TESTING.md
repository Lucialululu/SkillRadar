# Separate SkillRadar user-testing app

Copy `app_testing.py` to the **repository root**, alongside `app.py`.
Copy `skillradar/study_logging.py` to `skillradar/` if it is not there already.
Copy `tests/test_study_logging.py` to `tests/` if not already there.
Keep the regular `app.py` unchanged.

Run the participant app locally:

```bash
uv run streamlit run app_testing.py
```

The standard development app runs as before:

```bash
uv run streamlit run app.py
```

## Practice run

Use **Try an example CV**, finish the report and answer all six feedback questions. Use code `TEST01`, tick **Practice submission**, consent, and submit. The file `data/user_study/responses.csv` should contain the row with `test_run=True`.

To clear **all** responses (only do this before real participants, not afterward), stop the app and remove `data/user_study/responses.csv`.

## Important limitation

The CSV is written on the computer/server running Streamlit. This is appropriate for a local supervised pilot, **not** reliable permanent storage for an independently accessed Streamlit Community Cloud deployment. Before inviting remote participants, configure durable storage (e.g. a database) and test submissions from two separate browser sessions. Never commit raw participant results or CVs to public GitHub.

The current code prevents duplicate submissions within one browser session but does not prevent the same participant code being submitted in a separate session.
