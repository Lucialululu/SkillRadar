"""
Skill demand per role: "in what % of postings for this role does tool X appear?"

Two steps, so the app never touches the 5 GB job_summary.csv:

1. BUILD (offline, once, slow): run the matcher over every target-role posting and
   save one small table, one row per posting:
       data/processed/posting_tools_<source>.csv
       posting_id, source, role, level, country, title, tools ("Python;SQL;...")
   Rebuild whenever the matcher changes (new MANUAL_DROP etc.).

2. QUERY (fast, any time): filter that table by role / level / country and count.
   The same table is what the stability test (dataset A vs B) and bootstraps use.

Usage:
    python main.py build --source primary
    python main.py build --source secondary

    from skillradar.demand import load_posting_tools, demand_table
    pt = load_posting_tools("primary")
    demand_table(pt, "data scientist")
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from skillradar.matcher import KeywordMatcher

DATA = Path("data")
PROCESSED = DATA / "processed"
SOURCES = {
    "primary": DATA / "kagglev2",       # asaniczka 1.3M, Jan 2024
    "secondary": DATA / "kaggle",       # arshkon 124K, Apr 2024
}

# first matching pattern wins, matched against the posting title (case-insensitive)
ROLE_PATTERNS = {
    "data scientist":    r"data scien",
    "data analyst":      r"data analy",
    "software engineer": r"software (?:engineer|developer)",
    "ml engineer":       r"(?:machine learning|ml) engineer",
    "ux designer":       r"(?:ux|ui|user experience).*design",
}

# the two datasets name experience levels differently -> one shared vocabulary
LEVEL_MAP = {
    # primary (job_level)
    "mid senior": "mid-senior", "associate": "associate",
    # secondary (formatted_experience_level)
    "entry level": "entry", "internship": "internship",
    "mid-senior level": "mid-senior", "director": "director", "executive": "executive",
}
STUDENT_LEVELS = ("entry", "internship")

SEP = ";"   # tools are joined with this in the CSV (no O*NET tool name contains it)


# ---------------------------------------------------------------------------
# Roles and levels
# ---------------------------------------------------------------------------

def tag_role(titles: pd.Series) -> pd.Series:
    """First matching role per title, NaN if none."""
    role = pd.Series(np.nan, index=titles.index, dtype="object")
    for r, p in ROLE_PATTERNS.items():
        hit = role.isna() & titles.str.contains(p, case=False, regex=True, na=False)
        role[hit] = r
    return role


def resolve_role(text: str) -> str:
    """Free-text role from the user ("Data Scientist", "ML engineer") -> a ROLE_PATTERNS key."""
    t = text.strip().lower()
    if t in ROLE_PATTERNS:
        return t
    for r, p in ROLE_PATTERNS.items():
        if re.search(p, t):
            return r
    raise ValueError(f"Unknown role '{text}'. Available: {', '.join(ROLE_PATTERNS)}")


def normalise_level(level: pd.Series) -> pd.Series:
    return level.str.strip().str.lower().map(lambda x: LEVEL_MAP.get(x, x) if isinstance(x, str) else x)


# ---------------------------------------------------------------------------
# Step 1: BUILD the posting -> tools table (offline)
# ---------------------------------------------------------------------------

def build_primary(matcher: KeywordMatcher, folder: Path = SOURCES["primary"],
                  chunksize: int = 100_000) -> pd.DataFrame:
    """asaniczka dataset: titles in linkedin_job_postings.csv, text streamed from job_summary.csv."""
    meta = pd.read_csv(folder / "linkedin_job_postings.csv",
                       usecols=["job_link", "job_title", "job_level", "search_country"])
    meta = meta.drop_duplicates("job_link")
    meta["role"] = tag_role(meta["job_title"])
    meta = meta[meta["role"].notna()].set_index("job_link")

    rows = []
    for chunk in pd.read_csv(folder / "job_summary.csv", chunksize=chunksize):
        chunk = chunk[chunk["job_link"].isin(meta.index)].drop_duplicates("job_link")
        for link, text in zip(chunk["job_link"], chunk["job_summary"]):
            m = meta.loc[link]
            rows.append({
                "posting_id": link, "source": "primary", "role": m["role"],
                "level": m["job_level"], "country": m["search_country"], "title": m["job_title"],
                "tools": SEP.join(sorted(matcher.extract_tools(text))),
            })
    out = pd.DataFrame(rows)
    out["level"] = normalise_level(out["level"])
    return out


def build_secondary(matcher: KeywordMatcher, folder: Path = SOURCES["secondary"]) -> pd.DataFrame:
    """arshkon dataset: everything is in postings.csv (US only)."""
    cols = ["job_id", "title", "description", "skills_desc", "formatted_experience_level"]
    p = pd.read_csv(folder / "postings.csv", usecols=cols).drop_duplicates("job_id")
    p["role"] = tag_role(p["title"])
    p = p[p["role"].notna()]
    text = p["description"].fillna("") + "\n" + p["skills_desc"].fillna("")
    out = pd.DataFrame({
        "posting_id": p["job_id"], "source": "secondary", "role": p["role"],
        "level": normalise_level(p["formatted_experience_level"]),
        "country": "United States", "title": p["title"],
        "tools": [SEP.join(sorted(matcher.extract_tools(t))) for t in text],
    })
    return out.reset_index(drop=True)


def build(source: str, matcher: KeywordMatcher, out_dir: Path = PROCESSED) -> Path:
    df = {"primary": build_primary, "secondary": build_secondary}[source](matcher)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"posting_tools_{source}.csv"
    df.to_csv(path, index=False)
    return path


# ---------------------------------------------------------------------------
# Step 2: QUERY demand
# ---------------------------------------------------------------------------

def load_posting_tools(source: str = "primary", folder: Path = PROCESSED) -> pd.DataFrame:
    path = folder / f"posting_tools_{source}.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Build it first:  python main.py build --source {source}")
    df = pd.read_csv(path, keep_default_na=False, na_values={"level": [""], "country": [""]})
    df["tool_set"] = df["tools"].map(lambda s: set(s.split(SEP)) if s else set())
    return df


def filter_postings(pt: pd.DataFrame, role: str, levels: Iterable[str] | None = None,
                    country: str | None = None) -> pd.DataFrame:
    sub = pt[pt["role"] == role]
    if levels:
        sub = sub[sub["level"].isin(list(levels))]
    if country:
        sub = sub[sub["country"].str.lower() == country.lower()]
    return sub


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a proportion (behaves well near 0% and with small n)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def demand_from_sets(tool_sets: Iterable[set[str]]) -> pd.DataFrame:
    """Core computation: share of postings mentioning each tool (each posting counts once)."""
    tool_sets = list(tool_sets)
    n = len(tool_sets)
    counts = pd.Series([t for s in tool_sets for t in s], dtype="object").value_counts()
    rows = []
    for tool, k in counts.items():
        lo, hi = wilson(int(k), n)
        rows.append({"tool": tool, "n_with_tool": int(k), "share": k / n, "ci_low": lo, "ci_high": hi})
    df = pd.DataFrame(rows, columns=["tool", "n_with_tool", "share", "ci_low", "ci_high"])
    df.attrs["n_postings"] = n
    return df.sort_values(["share", "tool"], ascending=[False, True]).reset_index(drop=True)


def onet_flags(software: pd.DataFrame) -> pd.DataFrame:
    """Per tool: is it an O*NET Hot Technology / In Demand anywhere?"""
    f = software.groupby("Workplace Example")[["Hot Technology", "In Demand"]].agg(lambda s: (s == "Y").any())
    return f.rename(columns={"Hot Technology": "hot", "In Demand": "in_demand"})


def demand_table(pt: pd.DataFrame, role: str, levels: Iterable[str] | None = None,
                 country: str | None = None, software: pd.DataFrame | None = None) -> pd.DataFrame:
    """Demand for one role, optionally with O*NET flags. n is in df.attrs['n_postings']."""
    sub = filter_postings(pt, role, levels, country)
    df = demand_from_sets(sub["tool_set"])
    n = df.attrs["n_postings"]
    if software is not None:
        df = df.merge(onet_flags(software), left_on="tool", right_index=True, how="left")
        df[["hot", "in_demand"]] = df[["hot", "in_demand"]].fillna(False).astype(bool)
    df.attrs["n_postings"] = n
    df.attrs["role"] = role
    return df
