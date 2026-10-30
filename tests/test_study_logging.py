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
