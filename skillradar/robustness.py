"""
Goal 2: is the demand ranking robust, and how does it differ by seniority?

Works on the posting -> tools tables from `main.py build` (data/processed/posting_tools_*.csv),
so nothing here touches the raw data.

  replication()   same role, two independent datasets: Spearman rank correlation of tool shares
                  over the union of both top-k lists, with a bootstrap 95% interval
  rank_intervals() bootstrap 95% interval of each tool's rank within one dataset
  seniority()     entry/internship vs mid-senior postings in one dataset: difference in share per
                  tool, two-proportion z-test, Benjamini-Hochberg correction over the tools tested

    from skillradar.demand import load_posting_tools
    from skillradar.robustness import replication
    a, b = load_posting_tools("primary"), load_posting_tools("secondary")
    r = replication(a, b, "data scientist", country_a="United States")
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from skillradar.demand import filter_postings


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

def tool_matrix(sub: pd.DataFrame, tools: list[str]) -> np.ndarray:
    """postings x tools, 1 if the posting mentions the tool."""
    idx = {t: j for j, t in enumerate(tools)}
    X = np.zeros((len(sub), len(tools)), dtype=np.int8)
    for i, s in enumerate(sub["tool_set"]):
        for t in s:
            j = idx.get(t)
            if j is not None:
                X[i, j] = 1
    return X


def top_tools(sub: pd.DataFrame, k: int) -> list[str]:
    counts = pd.Series([t for s in sub["tool_set"] for t in s], dtype="object").value_counts()
    return counts.index[:k].tolist()


def spearman(x, y) -> float:
    x, y = pd.Series(x, dtype=float), pd.Series(y, dtype=float)
    if len(x) < 3 or x.nunique() < 2 or y.nunique() < 2:
        return float("nan")
    return float(np.corrcoef(x.rank(), y.rank())[0, 1])


def boot_shares(X: np.ndarray, n_boot: int, rng: np.random.Generator) -> np.ndarray:
    """n_boot x tools: shares in bootstrap resamples of the postings (multinomial weights)."""
    n = X.shape[0]
    W = rng.multinomial(n, np.full(n, 1 / n), size=n_boot)        # n_boot x n
    return (W @ X) / n


def p_two_sided(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2))


def benjamini_hochberg(p: Iterable[float]) -> np.ndarray:
    p = np.asarray(list(p), dtype=float)
    n = len(p)
    if n == 0:
        return p
    order = np.argsort(p)
    q = p[order] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.minimum(q, 1.0)
    return out


# ---------------------------------------------------------------------------
# Replication across datasets
# ---------------------------------------------------------------------------

@dataclass
class Replication:
    role: str
    n_a: int
    n_b: int
    rho: float
    ci: tuple[float, float]
    table: pd.DataFrame          # tool, share_a, share_b, rank_a, rank_b, diff_pp

    @property
    def small_sample(self) -> bool:
        return min(self.n_a, self.n_b) < 100


def replication(pt_a: pd.DataFrame, pt_b: pd.DataFrame, role: str, top: int = 20,
                levels_a=None, levels_b=None, country_a=None, country_b=None,
                n_boot: int = 1000, seed: int = 0) -> Replication:
    a = filter_postings(pt_a, role, levels_a, country_a)
    b = filter_postings(pt_b, role, levels_b, country_b)
    if len(a) == 0 or len(b) == 0:
        return Replication(role, len(a), len(b), float("nan"), (float("nan"),) * 2, pd.DataFrame())
    tools = list(dict.fromkeys(top_tools(a, top) + top_tools(b, top)))     # union, keeps order
    Xa, Xb = tool_matrix(a, tools), tool_matrix(b, tools)
    sa, sb = Xa.mean(0), Xb.mean(0)
    rho = spearman(sa, sb)

    rng = np.random.default_rng(seed)
    Ba, Bb = boot_shares(Xa, n_boot, rng), boot_shares(Xb, n_boot, rng)
    rhos = np.array([spearman(Ba[i], Bb[i]) for i in range(n_boot)])
    rhos = rhos[~np.isnan(rhos)]
    ci = (float(np.quantile(rhos, 0.025)), float(np.quantile(rhos, 0.975))) if len(rhos) else (np.nan, np.nan)

    table = pd.DataFrame({"tool": tools, "share_a": sa, "share_b": sb})
    table["rank_a"] = table["share_a"].rank(ascending=False, method="min").astype(int)
    table["rank_b"] = table["share_b"].rank(ascending=False, method="min").astype(int)
    table["diff_pp"] = (table["share_b"] - table["share_a"]) * 100
    table = table.sort_values("share_a", ascending=False).reset_index(drop=True)
    return Replication(role, len(a), len(b), rho, ci, table)


# ---------------------------------------------------------------------------
# Rank stability within one dataset
# ---------------------------------------------------------------------------

def rank_intervals(pt: pd.DataFrame, role: str, top: int = 20, candidates: int = 40,
                   levels=None, country=None, n_boot: int = 1000, seed: int = 0) -> pd.DataFrame:
    """Rank of each top tool among the `candidates` most common tools, with a bootstrap 95% interval.
    A tool whose interval is e.g. 3-4 has a stable position; 8-19 means 'somewhere in the middle'."""
    sub = filter_postings(pt, role, levels, country)
    tools = top_tools(sub, candidates)
    if not tools:
        return pd.DataFrame(columns=["tool", "share", "rank", "rank_lo", "rank_hi"])
    X = tool_matrix(sub, tools)
    B = boot_shares(X, n_boot, np.random.default_rng(seed))
    ranks = (-B).argsort(1).argsort(1) + 1                         # n_boot x tools, 1 = most common
    share = X.mean(0)
    df = pd.DataFrame({
        "tool": tools, "share": share,
        "rank": pd.Series(share).rank(ascending=False, method="min").astype(int).values,
        "rank_lo": np.quantile(ranks, 0.025, axis=0).astype(int),
        "rank_hi": np.quantile(ranks, 0.975, axis=0).astype(int),
    })
    df.attrs["n_postings"] = len(sub)
    return df.sort_values("rank").head(top).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Entry level vs senior
# ---------------------------------------------------------------------------

def seniority(pt: pd.DataFrame, role: str, low=("entry", "internship"), high=("mid-senior",),
              top: int = 20, country=None, alpha: float = 0.05) -> pd.DataFrame:
    """Per tool: share in junior vs senior postings for one role, difference with 95% CI,
    two-proportion z-test, BH-corrected q-value. Tools = union of both groups' top lists."""
    lo = filter_postings(pt, role, low, country)
    hi = filter_postings(pt, role, high, country)
    n1, n2 = len(lo), len(hi)
    cols = ["tool", "share_junior", "share_senior", "diff_pp", "ci_low_pp", "ci_high_pp", "z", "p", "q", "significant"]
    if n1 == 0 or n2 == 0:
        df = pd.DataFrame(columns=cols)
        df.attrs.update(n_junior=n1, n_senior=n2)
        return df
    tools = list(dict.fromkeys(top_tools(hi, top) + top_tools(lo, top)))
    p1, p2 = tool_matrix(lo, tools).mean(0), tool_matrix(hi, tools).mean(0)
    pooled = (p1 * n1 + p2 * n2) / (n1 + n2)
    se0 = np.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    z = np.divide(p2 - p1, se0, out=np.zeros_like(se0), where=se0 > 0)
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    p = np.array([p_two_sided(v) for v in z])
    df = pd.DataFrame({
        "tool": tools, "share_junior": p1, "share_senior": p2, "diff_pp": (p2 - p1) * 100,
        "ci_low_pp": (p2 - p1 - 1.96 * se) * 100, "ci_high_pp": (p2 - p1 + 1.96 * se) * 100,
        "z": z, "p": p, "q": benjamini_hochberg(p),
    })
    df["significant"] = df["q"] < alpha
    df.attrs.update(n_junior=n1, n_senior=n2)
    return df.sort_values("diff_pp", ascending=False).reset_index(drop=True)
