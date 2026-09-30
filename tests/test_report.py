"""Tests for skillradar.report."""
import pandas as pd
import pytest

from skillradar.demand import demand_from_sets
from skillradar.report import build_report, display_name, format_report


@pytest.mark.parametrize("tool, name", [
    ("Structured query language SQL", "SQL"),
    ("Amazon Web Services AWS software", "AWS"),
    ("Microsoft Power BI", "Power BI"),
    ("Microsoft Teams", "Microsoft Teams"),       # NO_SHORT keeps the vendor
    ("Rust programming language", "Rust"),
    ("Python", "Python"),
])
def test_display_name(tool, name):
    assert display_name(tool) == name


def _demand(n_extra=0):
    # Python 80%, SQL 60%, Tableau 20%, Rare 2% (of 100 + n_extra postings)
    sets = ([{"Python", "SQL", "Tableau"}] * 20 + [{"Python", "SQL"}] * 40 + [{"Python"}] * 20
            + [{"Rare"}] * 2 + [set()] * (18 + n_extra))
    d = demand_from_sets(sets)
    d.attrs["role"] = "data scientist"
    return d


def test_missing_ranked_by_demand_and_coverage_weighted():
    rep = build_report({"SQL", "Figma"}, _demand(), top=10, min_share=0.05)
    assert rep.missing["tool"].tolist() == ["Python", "Tableau"]
    assert rep.have["tool"].tolist() == ["SQL"]
    assert rep.coverage == pytest.approx(0.6 / (0.8 + 0.6 + 0.2))
    assert rep.other_cv_tools == ["Figma"]                    # on CV, not common for role
    assert "Rare" not in rep.missing["tool"].tolist()          # below min_share


def test_top_limits_comparison():
    rep = build_report(set(), _demand(), top=1)
    assert rep.missing["tool"].tolist() == ["Python"] and rep.coverage == 0


def test_format_report():
    text = format_report(build_report({"Python"}, _demand(), top=3))
    assert "data scientist (100 postings" in text
    assert "Tableau" in text and "missing" in text and "in 20% of postings" in text
    assert "!" not in text.splitlines()[1]                    # no small-sample warning at n=100


def test_small_sample_and_empty():
    d = demand_from_sets([{"Python"}] * 10)
    d.attrs["role"] = "ux designer"
    assert "Only 10 postings" in format_report(build_report(set(), d))
    empty = demand_from_sets([])
    empty.attrs["role"] = "ux designer"
    assert "No postings" in format_report(build_report(set(), empty))
