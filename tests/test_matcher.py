"""
Tests for skillradar.matcher. Run from the repo root with:  pytest

Rule of thumb: every time you find a false positive / missed skill in real data,
add the sentence here first (it should fail), then fix the matcher.

Most tests use a tiny fake O*NET table, so they run without the data/ folder.
The tests at the bottom use the real O*NET file and are skipped if it is missing.
"""
from pathlib import Path

import pandas as pd
import pytest

from skillradar.matcher import (
    KeywordMatcher, aliases, is_abbrev, is_generic, squash, tokens,
)

# ---------------------------------------------------------------------------
# Fixture: a small O*NET-like table (same columns as software_skills.csv)
# ---------------------------------------------------------------------------

ROWS = [  # (Workplace Example, Hot Technology, In Demand)
    ("Python", "Y", "Y"),
    ("Structured query language SQL", "Y", "Y"),
    ("Amazon Web Services AWS software", "Y", "N"),
    ("Microsoft Power BI", "Y", "N"),
    ("Microsoft Excel", "Y", "Y"),
    ("Microsoft Teams", "Y", "N"),
    ("Apache Spark", "Y", "N"),
    ("R", "Y", "N"),
    ("Go", "Y", "N"),
    ("C++", "Y", "N"),
    ("C#", "Y", "N"),
    ("Node.js", "Y", "N"),
    ("Scikit-learn", "Y", "N"),
    ("Docker", "Y", "Y"),
    ("Payroll software", "Y", "N"),        # generic category -> must be dropped
    ("Obscure Legacy Tool", "N", "N"),     # not hot / in demand -> not in vocab
]


@pytest.fixture
def software():
    return pd.DataFrame(ROWS, columns=["Workplace Example", "Hot Technology", "In Demand"])


@pytest.fixture
def m(software):
    return KeywordMatcher(software, manual_drop=[])


# ---------------------------------------------------------------------------
# Vocabulary building
# ---------------------------------------------------------------------------

def test_vocab_only_hot_or_in_demand_and_not_generic(m):
    assert "Python" in m.vocab
    assert "Obscure Legacy Tool" not in m.vocab
    assert "Payroll software" not in m.vocab


def test_acronym_alias_only_when_it_abbreviates():
    assert "SQL" in aliases("Structured query language SQL")
    assert "AWS" in aliases("Amazon Web Services AWS software")


def test_vendor_is_stripped_unless_ambiguous():
    assert "Power BI" in aliases("Microsoft Power BI")
    assert "Teams" not in aliases("Microsoft Teams")      # NO_SHORT


def test_is_abbrev():
    assert is_abbrev("SQL", ["Structured", "query", "language"])
    assert not is_abbrev("XYZ", ["Structured", "query", "language"])


def test_is_generic():
    assert is_generic("Payroll software")
    assert not is_generic("Microsoft Power BI")
    assert not is_generic("Rust programming language")   # KEEP exemption


def test_tokens_keep_special_names():
    assert tokens("C++, C#, Node.js and R&D") == ["C++", "C#", "Node.js", "and", "R&D"]


def test_squash():
    assert squash("scikit-learn") == squash("Scikit Learn") == "scikitlearn"
    assert squash("C++") == "c++"


# ---------------------------------------------------------------------------
# Matching free text (CVs and posting descriptions)
# ---------------------------------------------------------------------------

def test_basic_matches(m):
    found = m.extract_tools("Skills: Python, SQL, AWS, Power BI, Docker")
    assert found == {
        "Python", "Structured query language SQL", "Amazon Web Services AWS software",
        "Microsoft Power BI", "Docker",
    }


def test_matching_is_case_insensitive_for_normal_tools(m):
    assert m.extract_tools("PYTHON and docker") == {"Python", "Docker"}


@pytest.mark.parametrize("text", [
    "our R&D team",                 # R inside R&D
    "you excel at communication",   # excel as a verb
    "let's go to the office",       # go as a verb
    "rest assured, we're flexible",
])
def test_english_words_do_not_match(m, text):
    assert m.extract_tools(text) == set()


def test_case_sensitive_tools_match_with_right_case(m):
    assert m.extract_tools("Analysis in R and Excel, services in Go") == {"R", "Microsoft Excel", "Go"}


def test_programming_language_symbols(m):
    assert m.extract_tools("C++ and C# with Node.js") == {"C++", "C#", "Node.js"}


def test_vendor_and_full_name_are_one_tool(m):
    assert m.extract_tools("Apache Spark (Spark streaming)") == {"Apache Spark"}


def test_each_tool_counted_once(m):
    assert len(m.extract_tools("Python python PYTHON")) == 1


def test_non_string_input(m):
    assert m.extract_tools(None) == set()
    assert m.extract_tools(float("nan")) == set()


def test_explain_shows_which_alias_fired(m):
    assert m.explain("We use SQL") == {"sql": "Structured query language SQL"}


@pytest.mark.xfail(strict=True, reason="Known limitation: capitalised English word at sentence start")
def test_known_limitation_sentence_start(m):
    assert m.extract_tools("Go further with us.") == set()


# ---------------------------------------------------------------------------
# Matching the dataset's skill labels (the lowercase bug from the primary notebook)
# ---------------------------------------------------------------------------

def test_labels_lowercase_case_sensitive_tools(m):
    found = m.extract_tools_from_labels(["python", "r", "excel", "spark"])
    assert found == {"Python", "R", "Microsoft Excel", "Apache Spark"}


def test_labels_with_stripped_punctuation(m):
    assert m.extract_tools_from_labels(["scikitlearn"]) == {"Scikit-learn"}


def test_labels_fall_back_to_text_matching(m):
    assert m.extract_tools_from_labels(["python programming", "communication"]) == {"Python"}


def test_labels_ignore_empty_and_nan(m):
    assert m.extract_tools_from_labels(["", None, float("nan")]) == set()


# ---------------------------------------------------------------------------
# Manual drops and the safety net
# ---------------------------------------------------------------------------

def test_drop_in_any_case(m):
    m.drop("go")                                   # stored as "Go" (case-sensitive)
    assert m.extract_tools("Services in Go") == set()
    assert m.extract_tools_from_labels(["go"]) == set()   # label index is rebuilt too


def test_manual_drop_argument(software):
    m = KeywordMatcher(software, manual_drop=["Docker"])
    assert m.extract_tools("Docker") == set()
    assert "docker" in m.dropped


def test_suggest_drops_only_suggests(m):
    texts = ["Python", "Python and SQL", "Python", "Docker"]
    s = m.suggest_drops(texts, threshold=0.5)
    assert list(s.index) == ["python"]
    assert m.extract_tools("Python") == {"Python"}        # nothing removed automatically


# ---------------------------------------------------------------------------
# Real O*NET file (skipped when data/ is not downloaded)
# ---------------------------------------------------------------------------

REAL = Path(__file__).resolve().parents[1] / "data" / "onet" / "software_skills.csv"
needs_data = pytest.mark.skipif(not REAL.exists(), reason="data/onet/software_skills.csv not downloaded")


@pytest.fixture(scope="module")
def real():
    return KeywordMatcher.from_csv(REAL)


@needs_data
def test_real_vocab_size_is_sane(real):
    assert 250 < len(real.vocab) < 400


@needs_data
def test_real_data_scientist_cv(real):
    cv = ("MSc student at DTU. Python (pandas, scikit-learn, PyTorch), SQL, R, Git/GitHub, "
          "Docker, Power BI and Excel. Worked on an R&D project; excel at teamwork.")
    found = real.extract_tools(cv)
    for tool in ["Python", "Scikit-learn", "PyTorch", "Structured query language SQL", "R",
                 "Git", "GitHub", "Docker", "Microsoft Power BI", "Microsoft Excel"]:
        assert tool in found, tool
