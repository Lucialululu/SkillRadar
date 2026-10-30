import csv
from pathlib import Path
import pytest
from skillradar.study_logging import save_response

def test_saves_anonymous_row(tmp_path):
    out = tmp_path / "results.csv"
    record = dict(participant_id="TEST01", test_run=True, role="data scientist",
                  dataset="all", detected=5, added=1, removed=2,
                  accuracy=4, relevance=4, usefulness=5,
                  explanation=3, trust=4, ease_of_use=5)
    save_response(record, path=out)
    with out.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["participant_id"] == "TEST01"
    assert rows[0]["removed"] == "2"
    assert "cv_text" not in rows[0]

def test_rejects_personal_cv_fields(tmp_path):
    with pytest.raises(ValueError, match="Unexpected"):
        save_response({"participant_id":"TEST02", "cv_text":"private"}, tmp_path / "x.csv")


class FakeSheet:
    """Stands in for a gspread worksheet: same two methods, rows kept in memory."""
    def __init__(self, rows=None):
        self.rows = rows or []

    def row_values(self, i):
        return self.rows[i - 1] if len(self.rows) >= i else []

    def append_row(self, values, value_input_option="RAW"):
        self.rows.append([str(v) for v in values])


def test_sheet_gets_header_once_then_rows(tmp_path):
    from skillradar.study_logging import FIELDS
    sheet = FakeSheet()
    for pid in ("P01", "P02"):
        where = save_response({"participant_id": pid, "accuracy": 4, "cv_type": "own",
                               "main_confusion": "the  ranges\nwere unclear"}, path=tmp_path / "x.csv", sheet=sheet)
        assert where == "sheet"
    assert sheet.rows[0] == FIELDS and len(sheet.rows) == 3
    row = dict(zip(FIELDS, sheet.rows[2]))
    assert row["participant_id"] == "P02" and row["accuracy"] == "4"
    assert row["main_confusion"] == "the ranges were unclear"     # one line in the sheet
    assert not (tmp_path / "x.csv").exists()                         # nothing written locally


def test_sheet_with_other_content_is_refused():
    with pytest.raises(ValueError, match="header"):
        save_response({"participant_id": "P01"}, sheet=FakeSheet([["something", "else"]]))


def test_free_text_is_capped(tmp_path):
    out = tmp_path / "r.csv"
    save_response({"participant_id": "P01", "suggested_improvement": "x" * 5000}, path=out)
    with out.open(newline="", encoding="utf-8") as f:
        assert len(next(csv.DictReader(f))["suggested_improvement"]) == 1000


def test_no_sheet_configured_means_local_csv():
    from skillradar.study_logging import sheet_from_secrets
    assert sheet_from_secrets({}) is None
