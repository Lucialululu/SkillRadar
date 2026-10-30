"""Anonymous user-study results. Never store CV text or file names.

Where a result goes:
  * a Google Sheet, when the app has one configured in its Streamlit secrets (`[gsheets]`, see
    user_testing/README_TESTING.md). Use this for the hosted app: a hosted server's disk is wiped
    on every restart, the sheet is not, and the whole team sees new rows live.
  * otherwise data/user_study/responses.csv on the computer running the app (gitignored).
Both use the same columns, so results can be combined later.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

RESULTS = Path("data/user_study/responses.csv")  # data/ is gitignored in SkillRadar
FIELDS = [
    "participant_id", "test_run", "recorded_at_utc", "cv_type", "role", "dataset",
    "detected", "added", "removed",
    "accuracy", "relevance", "usefulness", "explanation", "trust", "ease_of_use",
    "main_confusion", "suggested_improvement",
]
_FIELDS = FIELDS            # old name, kept for code that imported it
FREE_TEXT = ("main_confusion", "suggested_improvement")
MAX_TEXT = 1000             # long enough for a comment, too short for a pasted CV
_LOCK = Lock()


def _row(record: dict) -> dict:
    """Validate one result and turn it into a full row (unknown fields are refused)."""
    unexpected = set(record) - (set(FIELDS) - {"recorded_at_utc"})
    if unexpected:
        raise ValueError(f"Unexpected fields: {sorted(unexpected)}")
    if not str(record.get("participant_id", "")).strip():
        raise ValueError("A participant ID is required")
    row = {key: record.get(key, "") for key in FIELDS}
    for key in FREE_TEXT:
        row[key] = " ".join(str(row[key]).split())[:MAX_TEXT]   # one line, capped
    row["recorded_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return row


def save_response(record: dict, path: Path = RESULTS, sheet=None) -> str:
    """Append one anonymous result. Returns where it went: "sheet" or "csv".

    `sheet` is a gspread worksheet (or anything with row_values / append_row); None = local CSV."""
    row = _row(record)
    if sheet is not None:
        with _LOCK:
            if sheet.row_values(1) != FIELDS:            # empty sheet: write the header first
                if sheet.row_values(1):
                    raise ValueError("The sheet's first row is not the expected header; use an empty sheet")
                sheet.append_row(FIELDS, value_input_option="RAW")
            sheet.append_row([str(row[k]) for k in FIELDS], value_input_option="RAW")
        return "sheet"
    path = Path(path)
    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        is_new = not path.exists() or path.stat().st_size == 0
        with path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            if is_new:
                writer.writeheader()
            writer.writerow(row)
    return "csv"


def sheet_from_secrets(secrets):
    """Open the study sheet from Streamlit secrets, or return None when none is configured.

    Expects a [gsheets] table with `sheet_id` plus the service-account JSON fields."""
    if "gsheets" not in secrets:
        return None
    import gspread                                       # only needed when a sheet is configured
    cfg = dict(secrets["gsheets"])
    sheet_id = cfg.pop("sheet_id")
    return gspread.service_account_from_dict(cfg).open_by_key(sheet_id).sheet1
