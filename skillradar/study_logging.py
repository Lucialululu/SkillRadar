"""Anonymous, server-local user study results. Never store CV text or filenames."""
from __future__ import annotations
import csv
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

RESULTS = Path("data/user_study/responses.csv")  # data/ is gitignored in SkillRadar
_FIELDS = [
    "participant_id", "test_run", "recorded_at_utc", "role", "dataset",
    "detected", "added", "removed",
    "accuracy", "relevance", "usefulness", "explanation", "trust", "ease_of_use",
]
_LOCK = Lock()


def save_response(record: dict, path: Path = RESULTS) -> None:
    """Append one anonymous result. Reject unexpected data fields."""
    unexpected = set(record) - (set(_FIELDS) - {"recorded_at_utc"})
    if unexpected:
        raise ValueError(f"Unexpected fields: {sorted(unexpected)}")
    if not str(record.get("participant_id", "")).strip():
        raise ValueError("A participant ID is required")
    row = {key: record.get(key, "") for key in _FIELDS}
    row["recorded_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path = Path(path)
    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        is_new = not path.exists() or path.stat().st_size == 0
        with path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=_FIELDS)
            if is_new:
                writer.writeheader()
            writer.writerow(row)
