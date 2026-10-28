"""Tests for the evaluation code: ablation variants, label normalisation, metrics.
Uses a small fake O*NET table, so no data/ folder is needed."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))

import evaluate as ev  # noqa: E402
from skillradar.variants import STEPS, make_matcher  # noqa: E402

ROWS = [
    ("Python", "Y", "Y"), ("Structured query language SQL", "Y", "Y"),
    ("Amazon Web Services AWS software", "Y", "N"), ("Microsoft Power BI", "Y", "N"),
    ("R", "Y", "N"), ("Go", "Y", "N"), ("Microsoft Excel", "Y", "Y"),
]


@pytest.fixture
def software():
    return pd.DataFrame(ROWS, columns=["Workplace Example", "Hot Technology", "In Demand"])


TEXT = "We use Python, SQL and AWS, dashboards in Power BI, models in R. Go further and excel at teamwork."


def test_ablation_steps_add_recall_in_order(software):
    found = {s: make_matcher(software, s, manual_drop=[]).extract_tools(TEXT) for s in STEPS}
    assert found["exact"] == {"Python", "R", "Go"}      # exact names, but case-insensitive: "Go further" fires
    assert "Microsoft Power BI" in found["vendor"] and "Structured query language SQL" not in found["vendor"]
    assert {"Structured query language SQL", "Amazon Web Services AWS software"} <= found["acronym"]
    # without case rules "Go further" and "excel at" fire; the full matcher keeps R, drops "excel at"
    assert {"Go", "Microsoft Excel"} <= found["acronym"]
    assert "R" in found["full"] and "Microsoft Excel" not in found["full"]


def test_label_normaliser(software):
    norm = ev.LabelNormaliser(software)
    assert norm("SQL") == "Structured query language SQL"
    assert norm("power bi") == "Microsoft Power BI"
    assert norm(" AWS ") == "Amazon Web Services AWS software"
    assert norm("r") == "R"                      # labels are standalone names, case does not matter
    assert norm("Jupyter") == ev.OOV + "Jupyter"


def test_parse_tools_accepts_semicolons_and_commas():
    assert ev.parse_tools("Python; SQL,  AWS;") == ["Python", "SQL", "AWS"]
    assert ev.parse_tools(None) == []


def test_scoring_separates_out_of_vocabulary():
    c = ev.score_item(found={"Python", "Go"}, truth={"Python", "R", ev.OOV + "Jupyter"})
    assert (c.tp, c.fp, c.fn_vocab, c.fn_oov) == (1, 1, 1, 1)
    assert c.precision == 0.5 and c.recall_vocab == 0.5 and c.recall_all == pytest.approx(1 / 3)


def test_bootstrap_interval_contains_point_estimate():
    counts = [ev.Counts(tp=3, fp=1), ev.Counts(tp=2, fp=0), ev.Counts(tp=1, fp=2)]
    lo, hi = ev.bootstrap_ci(counts, "precision", n_boot=500)
    assert lo <= ev.total(counts).precision <= hi


def test_kappa():
    assert ev.kappa([True, False, True, False], [True, False, True, False]) == 1.0
    assert ev.kappa([True, True, False, False], [True, False, True, False]) == 0.0
