"""Tests for skillradar.demand (synthetic data, no data/ folder needed)."""
import pandas as pd
import pytest

from skillradar.demand import (
    build_primary, build_secondary, demand_from_sets, demand_table, filter_postings,
    load_posting_tools, normalise_level, resolve_role, tag_role, wilson,
)
from skillradar.matcher import KeywordMatcher

SOFTWARE = pd.DataFrame(
    [("Python", "Y", "Y"), ("Structured query language SQL", "Y", "Y"), ("Docker", "Y", "N"),
     ("R", "Y", "N")],
    columns=["Workplace Example", "Hot Technology", "In Demand"],
)


@pytest.fixture
def m():
    return KeywordMatcher(SOFTWARE, manual_drop=[])


def test_tag_role():
    titles = pd.Series(["Senior Data Scientist", "Software Developer II", "Nurse", "Machine Learning Engineer"])
    assert tag_role(titles).tolist()[:2] == ["data scientist", "software engineer"]
    assert pd.isna(tag_role(titles)[2])
    assert tag_role(titles)[3] == "ml engineer"


def test_resolve_role():
    assert resolve_role("Data Scientist") == "data scientist"
    assert resolve_role("junior ML engineer") == "ml engineer"
    with pytest.raises(ValueError, match="Available"):
        resolve_role("barista")


def test_normalise_level_maps_both_datasets():
    s = pd.Series(["Mid senior", "Entry level", "Internship", "Mid-Senior level", None])
    assert normalise_level(s).tolist()[:4] == ["mid-senior", "entry", "internship", "mid-senior"]


def test_wilson():
    lo, hi = wilson(50, 100)
    assert lo < 0.5 < hi and round(lo, 2) == 0.40 and round(hi, 2) == 0.60
    assert wilson(0, 10)[0] == 0.0 and wilson(0, 0) == (0.0, 0.0)


def test_demand_counts_each_posting_once():
    df = demand_from_sets([{"Python", "SQL"}, {"Python"}, set(), {"Python"}])
    assert df.attrs["n_postings"] == 4
    assert df.set_index("tool")["share"].to_dict() == {"Python": 0.75, "SQL": 0.25}


def _posting_tools():
    return pd.DataFrame({
        "role": ["data scientist"] * 3 + ["data analyst"],
        "level": ["entry", "mid-senior", "entry", "entry"],
        "country": ["United States", "United Kingdom", "United States", "United States"],
        "tool_set": [{"Python"}, {"Python", "Docker"}, {"R"}, {"Structured query language SQL"}],
    })


def test_filter_and_demand_table():
    pt = _posting_tools()
    assert len(filter_postings(pt, "data scientist", levels=["entry"], country="united states")) == 2
    d = demand_table(pt, "data scientist", software=SOFTWARE)
    assert d.attrs == {"n_postings": 3, "role": "data scientist"}
    assert d.iloc[0]["tool"] == "Python" and bool(d.iloc[0]["in_demand"])
    assert not bool(d.set_index("tool").loc["Docker", "in_demand"])


def test_build_primary_and_roundtrip(tmp_path, m):
    links = [f"https://linkedin.com/jobs/view/{i}" for i in range(3)]
    pd.DataFrame({"job_link": links, "job_title": ["Data Scientist", "Nurse", "Data Analyst"],
                  "job_level": ["Mid senior", "Associate", "Associate"],
                  "search_country": ["United States"] * 3}).to_csv(tmp_path / "linkedin_job_postings.csv", index=False)
    pd.DataFrame({"job_link": links, "job_summary": ["Python and R&D", "Python", "no tools"]}).to_csv(
        tmp_path / "job_summary.csv", index=False)

    out = build_primary(m, folder=tmp_path, chunksize=2)
    assert out["role"].tolist() == ["data scientist", "data analyst"]       # nurse dropped
    assert out["tools"].tolist() == ["Python", ""]                           # "R&D" is not R
    assert out["level"].tolist() == ["mid-senior", "associate"]

    out.to_csv(tmp_path / "posting_tools_primary.csv", index=False)
    pt = load_posting_tools("primary", folder=tmp_path)
    assert pt["tool_set"].tolist() == [{"Python"}, set()]


def test_build_secondary_uses_description_and_skills_desc(tmp_path, m):
    pd.DataFrame({"job_id": [1, 2], "title": ["Data Scientist", "Barista"],
                  "description": ["We use Python.", "Coffee"], "skills_desc": ["Docker", None],
                  "formatted_experience_level": ["Entry level", "Internship"]}).to_csv(
        tmp_path / "postings.csv", index=False)
    out = build_secondary(m, folder=tmp_path)
    assert len(out) == 1 and out.loc[0, "tools"] == "Docker;Python" and out.loc[0, "level"] == "entry"


def test_missing_processed_file_gives_helpful_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="python main.py build"):
        load_posting_tools("primary", folder=tmp_path)


def test_role_patterns_use_word_boundaries():
    titles = pd.Series(["Sr. Structural Engineer - Building Design", "Printed Circuit Board Design Engineer",
                        "Luxury Design Sales Consultant", "SLD Fluids Design Engineer",
                        "UX/UI Designer", "Graphic Designer & UXUI Web Designer", "Senior UI Designer",
                        "User Experience Designer", "HTML Engineer"])
    roles = tag_role(titles).tolist()
    assert all(pd.isna(r) for r in roles[:4])
    assert roles[4:8] == ["ux designer"] * 4
    assert pd.isna(roles[8])                                   # not an "ml engineer"


def test_text_hash_ignores_case_and_whitespace():
    from skillradar.demand import text_hash
    assert text_hash("We use  Python.\n") == text_hash("we use python.")
    assert text_hash("We use Python.") != text_hash("We use R.")
    assert text_hash("") == text_hash(None) == ""


def test_load_dedups_identical_ads_within_role(tmp_path):
    pd.DataFrame({
        "posting_id": [1, 2, 3, 4, 5], "source": "secondary",
        "role": ["data scientist", "data scientist", "data analyst", "data scientist", "data scientist"],
        "level": "entry", "country": "United States", "title": ["a", "b", "c", "d", "e"],
        "company": "X", "text_hash": ["h1", "h1", "h1", "", ""], "tools": ["Python"] * 5,
    }).to_csv(tmp_path / "posting_tools_secondary.csv", index=False)
    pt = load_posting_tools("secondary", folder=tmp_path)
    assert pt["posting_id"].tolist() == [1, 3, 4, 5]          # same ad in another role is kept, empty text never merged
    assert pt.attrs["n_duplicates"] == 1
    assert len(load_posting_tools("secondary", folder=tmp_path, dedup=False)) == 5


def test_old_tables_without_hash_warn(tmp_path):
    pd.DataFrame({"posting_id": [1], "source": "primary", "role": "data scientist", "level": "",
                  "country": "", "title": "a", "tools": "Python"}).to_csv(
        tmp_path / "posting_tools_primary.csv", index=False)
    with pytest.warns(UserWarning, match="rebuild"):
        load_posting_tools("primary", folder=tmp_path)


def test_build_writes_hash_and_company(tmp_path, m):
    pd.DataFrame({"job_id": [1, 2], "title": ["Data Scientist", "Data Scientist II"],
                  "description": ["We use Python.", "We use  python."], "skills_desc": [None, None],
                  "formatted_experience_level": ["Entry level", "Entry level"],
                  "company_name": ["Acme", "Acme"]}).to_csv(tmp_path / "postings.csv", index=False)
    out = build_secondary(m, folder=tmp_path)
    assert out["company"].tolist() == ["Acme", "Acme"]
    assert out.loc[0, "text_hash"] == out.loc[1, "text_hash"] != ""
