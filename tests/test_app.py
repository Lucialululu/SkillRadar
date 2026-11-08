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


@pytest.mark.parametrize("app", ["app.py", "app_testing.py"])
def test_report_renders_have_first_with_range_key(app):
    """Both apps reach the report without errors; the report shows the tools you have before the missing ones
    and explains the 95% range (peer-pilot feedback)."""
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / app), default_timeout=120)
    at.session_state.step = 4
    at.session_state.cv_text, at.session_state.cv_name, at.session_state.cv_key = "Python, SQL and Tableau", "cv.txt", "t"
    at.run()
    assert not at.exception
    page = "".join(m.value for m in at.markdown)
    assert page.index("Already on your CV") < page.index("Missing, most requested first")
    assert "the 95% range" in page and 'class="sr-radar"' in page


@pytest.mark.parametrize("app", ["app.py", "app_testing.py"])
def test_report_starts_with_role_overview_without_repetition(app):
    """Peer feedback: 'which jobs can I apply for?' The page answers that first (one row per role,
    text verdicts, no emoji), then the chosen role's report; 'View' switches the report to another role."""
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / app), default_timeout=120)
    at.session_state.step = 4
    at.session_state.cv_text, at.session_state.cv_name, at.session_state.cv_key = "Python, SQL and Tableau", "cv.txt", "t"
    at.run()
    assert not at.exception
    page = "".join(m.value for m in at.markdown)
    assert page.count('class="sr-match') == 5 and "Shown below" in page
    assert sum(str(b.key).startswith("job:") for b in at.button) == 4      # a View button for every other role
    assert "How your CV matches each role" in page and "You can apply" not in page
    assert not any(ch in page for ch in "🟢🟡⚪")
    assert page.index("How your CV matches each role") < page.index("Already on your CV")
    assert "Skills you are missing" not in page                        # the old per-job details are gone
    before = at.session_state.role
    at.button(key=next(b.key for b in at.button if str(b.key).startswith("job:"))).click().run()
    assert not at.exception and at.session_state.role != before


def test_testing_app_asks_about_missing_tools_and_has_facilitator_part():
    """Peer trial: perceived accuracy, task success and facilitator notes are part of the saved form."""
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "app_testing.py"), default_timeout=120)
    at.session_state.step = 4
    at.session_state.cv_text, at.session_state.cv_name, at.session_state.cv_key = "Python, SQL and Tableau", "cv.txt", "t"
    at.run()
    assert not at.exception
    keys = {str(w.key) for w in [*at.selectbox, *at.multiselect, *at.text_area]}
    assert {"q_not_missing", "q_facilitator_notes", "q_task1_upload_role", "q_task4_choose_tool"} <= keys
    assert len(at.multiselect(key="q_not_missing").options) > 0       # the missing tools from the report
