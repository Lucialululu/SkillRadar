"""Tests for skillradar.robustness on synthetic posting tables (no data/ needed)."""
import random

import numpy as np
import pandas as pd
import pytest

from skillradar.robustness import (
    benjamini_hochberg, rank_intervals, replication, seniority, spearman, tool_matrix,
)

SHARES = {"Python": 0.8, "SQL": 0.55, "R": 0.45, "AWS": 0.25, "Tableau": 0.2,
          "Spark": 0.15, "Docker": 0.08, "Git": 0.05}


def fake_postings(n, shares, role="data scientist", level="mid-senior", country="United States", seed=0):
    rng = random.Random(seed)
    sets = [{t for t, p in shares.items() if rng.random() < p} for _ in range(n)]
    return pd.DataFrame({"role": role, "level": level, "country": country, "tool_set": sets})


def test_spearman():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    assert np.isnan(spearman([1, 1, 1], [1, 2, 3]))


def test_tool_matrix():
    df = pd.DataFrame({"tool_set": [{"A", "B"}, {"B"}, set()]})
    assert tool_matrix(df, ["A", "B", "C"]).tolist() == [[1, 1, 0], [0, 1, 0], [0, 0, 0]]


def test_replication_high_for_same_distribution_low_for_shuffled():
    a = fake_postings(2000, SHARES, seed=1)
    b = fake_postings(1000, SHARES, seed=2)
    r = replication(a, b, "data scientist", top=8, n_boot=200)
    assert r.rho > 0.9 and r.ci[0] <= r.rho <= r.ci[1]
    assert (r.n_a, r.n_b) == (2000, 1000) and not r.small_sample

    reversed_shares = dict(zip(SHARES, list(SHARES.values())[::-1]))
    c = fake_postings(1000, reversed_shares, seed=3)
    assert replication(a, c, "data scientist", top=8, n_boot=100).rho < 0


def test_replication_respects_filters_and_empty():
    a = fake_postings(300, SHARES, country="Canada")
    b = fake_postings(300, SHARES)
    r = replication(a, b, "data scientist", country_a="United States", n_boot=50)
    assert r.n_a == 0 and np.isnan(r.rho)


def test_rank_intervals_contain_rank_and_order():
    ri = rank_intervals(fake_postings(3000, SHARES), "data scientist", top=5, n_boot=200)
    assert ri["tool"].tolist()[:2] == ["Python", "SQL"]
    assert (ri["rank_lo"] <= ri["rank"]).all() and (ri["rank"] <= ri["rank_hi"]).all()
    assert ri.loc[0, "rank_hi"] == 1          # Python is clearly first


def test_seniority_finds_real_difference_only():
    junior = fake_postings(800, {**SHARES, "Docker": 0.05}, level="entry", seed=4)
    senior = fake_postings(800, {**SHARES, "Docker": 0.30}, level="mid-senior", seed=5)
    s = seniority(pd.concat([junior, senior]), "data scientist", top=8)
    sig = set(s.loc[s["significant"], "tool"])
    assert "Docker" in sig
    assert len(sig) <= 2                       # BH keeps false positives rare
    assert s.attrs == {"n_junior": 800, "n_senior": 800}


def test_benjamini_hochberg():
    q = benjamini_hochberg([0.01, 0.04, 0.03, 0.5])
    assert q.tolist() == pytest.approx([0.04, 0.0533, 0.0533, 0.5], abs=1e-3)
