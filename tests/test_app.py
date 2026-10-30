"""End-to-end check of the Streamlit flow (needs the built data in data/; skipped otherwise)."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NEEDED = [ROOT / "data/onet/software_skills.csv",
          ROOT / "data/processed/posting_tools_primary.csv",
          ROOT / "data/processed/posting_tools_secondary.csv"]
pytestmark = pytest.mark.skipif(not all(p.exists() for p in NEEDED), reason="built data not in data/")


def _role_step():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120)
    at.session_state.step = 2
    at.session_state.cv_text, at.session_state.cv_name = "Python, SQL", "cv.txt"
    return at.run()


def test_role_counts_follow_the_dataset_choice_immediately():
    """Regression: the posting counts on the role cards used to lag one click behind 'Compare against'."""
    at = _role_step()
    roles, datasets = at.radio[0], at.radio[1]

    def counts():
        return [int(c.split()[0].replace(",", "")) for c in at.radio[0].proto.captions]

    all_counts = counts()
    datasets.set_value("Entry level & internships").run()
    entry_counts = counts()
    at.radio[1].set_value("All experience levels").run()

    assert len(roles.options) == len(all_counts)
    assert all(e < a for e, a in zip(entry_counts, all_counts))   # the entry subset is smaller for every role
    assert counts() == all_counts                                  # and switching back restores it at once
