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
    # added for the peer trial (appended, so rows saved before keep their columns)
    "missing_shown", "missing_agreed",
    "task1_upload_role", "task2_correct_tools", "task3_understand_report", "task4_choose_tool",
    "facilitator_notes",
]
TASK_CODES = ("no_help", "with_help", "failed")
TASK_FIELDS = ("task1_upload_role", "task2_correct_tools", "task3_understand_report", "task4_choose_tool")
_FIELDS = FIELDS            # old name, kept for code that imported it
FREE_TEXT = ("main_confusion", "suggested_improvement", "facilitator_notes")
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
    for key in TASK_FIELDS:
        if row[key] not in ("", None, *TASK_CODES):
            raise ValueError(f"{key} must be one of {TASK_CODES}, not {row[key]!r}")
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
            header = sheet.row_values(1)
            if header != FIELDS:
                if not header:                               # empty sheet: write the header first
                    sheet.append_row(FIELDS, value_input_option="RAW")
                elif header == FIELDS[:len(header)]:         # older header: new columns were added at the end
                    sheet.update(values=[FIELDS], range_name="A1")
                else:
                    raise ValueError("The sheet's first row is not the expected header; use an empty sheet")
            sheet.append_row([str(row[k]) for k in FIELDS], value_input_option="RAW")
        return "sheet"
    path = Path(path)
    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        is_new = not path.exists() or path.stat().st_size == 0
        if not is_new:
            _upgrade_csv_header(path)
        with path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            if is_new:
                writer.writeheader()
            writer.writerow(row)
    return "csv"


def _upgrade_csv_header(path: Path) -> None:
    """A local results file from before new columns were added: rewrite it with the current header."""
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header = rows[0] if rows else []
    if header == FIELDS:
        return
    if header != FIELDS[:len(header)]:
        raise ValueError(f"{path} has an unexpected header; move it away and start a new file")
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        w.writerows(r + [""] * (len(FIELDS) - len(r)) for r in rows[1:])


def sheet_from_secrets(secrets):
    """Open the study sheet from Streamlit secrets, or return None when none is configured.

    Expects a [gsheets] table with `sheet_id` plus the service-account JSON fields."""
    if "gsheets" not in secrets:
        return None
    import gspread                                       # only needed when a sheet is configured
    cfg = dict(secrets["gsheets"])
    sheet_id = cfg.pop("sheet_id")
    return gspread.service_account_from_dict(cfg).open_by_key(sheet_id).sheet1
