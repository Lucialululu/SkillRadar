"""
Skill-gap report: CV tools vs. demand for a role.

    from skillradar.report import build_report, format_report
    rep = build_report(cv_tools, demand_df, top=15)
    print(format_report(rep))
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

from skillradar.matcher import KEEP, NO_SHORT, VENDORS, is_abbrev

SMALL_SAMPLE = 100   # warn below this many postings
STRONG_AT = 0.50     # role overview: "Strong match" from this coverage up
PARTIAL_AT = 0.30    # ... "Partial match" from this coverage up
# Wording on purpose: coverage of the tools postings name says nothing about being hired, so the
# overview describes the fit of the CV's tools, never "you can apply".


def display_name(tool: str) -> str:
    """Readable name for an O*NET tool: 'Structured query language SQL' -> 'SQL',
    'Microsoft Power BI' -> 'Power BI', 'Amazon Web Services AWS software' -> 'AWS'."""
    if tool in KEEP:
        return KEEP[tool]
    core = re.sub(r"\s+software$", "", tool, flags=re.I)
    words = core.split()
    if len(words) > 2 and re.fullmatch(r"[A-Z][A-Z0-9+#]{1,5}", words[-1]) and is_abbrev(words[-1], words[:-1]):
        return words[-1]
    for v in VENDORS:
        if core.startswith(v + " ") and core[len(v) + 1:].lower() not in NO_SHORT:
            return core[len(v) + 1:]
    return core


@dataclass
class SkillGapReport:
    role: str
    n_postings: int
    top: int
    coverage: float                                   # share-weighted, 0..1
    missing: pd.DataFrame                             # top tools the CV lacks, by demand
    have: pd.DataFrame                                # top tools the CV has
    other_cv_tools: list[tuple[str, float]] = field(default_factory=list)  # on CV, outside the top list
    note: str = ""

    @property
    def small_sample(self) -> bool:
        return self.n_postings < SMALL_SAMPLE


def build_report(cv_tools: set[str], demand: pd.DataFrame, top: int = 15,
                 min_share: float = 0.05, note: str = "") -> SkillGapReport:
    """Compare the CV's tools with the `top` most-demanded tools for the role.

    coverage = (sum of demand of the top tools you have) / (sum of demand of all top tools),
    so missing Python (in 79% of postings) costs more than missing Tableau (21%).
    """
    n = demand.attrs.get("n_postings", 0)
    role = demand.attrs.get("role", "?")
    ranked = demand[demand["share"] >= min_share].head(top).copy()
    ranked["on_cv"] = ranked["tool"].isin(cv_tools)

    total = ranked["share"].sum()
    coverage = float(ranked.loc[ranked["on_cv"], "share"].sum() / total) if total else 0.0

    # every CV tool that is not in the compared top list, with its share (0 if never seen)
    shares = demand.set_index("tool")["share"]
    other = sorted(((t, float(shares.get(t, 0.0))) for t in cv_tools if t not in set(ranked["tool"])),
                   key=lambda x: (-x[1], display_name(x[0])))

    return SkillGapReport(
        role=role, n_postings=n, top=top, coverage=coverage,
        missing=ranked[~ranked["on_cv"]].drop(columns="on_cv").reset_index(drop=True),
        have=ranked[ranked["on_cv"]].drop(columns="on_cv").reset_index(drop=True),
        other_cv_tools=other, note=note,
    )


@dataclass
class JobMatch:
    """One row of the job overview: how well the CV fits one role."""
    role: str
    n_postings: int
    have_pct: float                                   # = coverage of the role's top tools, 0..1
    have: list[str]                                   # top tools on the CV, most requested first
    missing: list[str]                                # top tools not on the CV, most requested first
    have_rows: pd.DataFrame = field(default_factory=pd.DataFrame, repr=False)     # share + 95% range per tool
    missing_rows: pd.DataFrame = field(default_factory=pd.DataFrame, repr=False)

    @property
    def missing_pct(self) -> float:
        return 1.0 - self.have_pct

    @property
    def verdict(self) -> str:
        if self.have_pct >= STRONG_AT:
            return "Strong match"
        if self.have_pct >= PARTIAL_AT:
            return "Partial match"
        return "Low match"


def job_matches(cv_tools: set[str], demands: dict[str, pd.DataFrame], top: int = 15,
                min_share: float = 0.05) -> list[JobMatch]:
    """Compare the CV with every role at once, best match first.

    demands: role -> demand_table(...) for that role. Uses the same coverage as build_report,
    so the percentage for the chosen role matches the big score on the report page.
    Roles with no postings are left out.
    """
    out = []
    for role, demand in demands.items():
        if demand.attrs.get("n_postings", 0) == 0:
            continue
        rep = build_report(cv_tools, demand, top=top, min_share=min_share)
        out.append(JobMatch(role=role, n_postings=rep.n_postings, have_pct=rep.coverage,
                            have=list(rep.have["tool"]), missing=list(rep.missing["tool"]),
                            have_rows=rep.have, missing_rows=rep.missing))
    return sorted(out, key=lambda m: (-m.have_pct, m.role))


def _flag(row) -> str:
    flags = [name for col, name in (("hot", "Hot Technology"), ("in_demand", "In Demand"))
             if col in row and bool(row[col])]
    return f"O*NET {' + '.join(flags)}" if flags else ""


def format_report(rep: SkillGapReport) -> str:
    lines = [f"SkillRadar: {rep.role} ({rep.n_postings:,} postings{', ' + rep.note if rep.note else ''})"]
    if rep.n_postings == 0:
        return lines[0] + "\nNo postings match this role/filter, nothing to compare against."
    if rep.small_sample:
        lines.append(f"! Only {rep.n_postings} postings: percentages are rough, see the ranges.")
    lines.append(f"Your CV covers {rep.coverage:.0%} of the demand for the top {rep.top} tools.\n")

    width = max([len(display_name(t)) for t in pd.concat([rep.missing, rep.have])["tool"]] + [8])

    def row(r, status):
        pct = f"in {r['share']:.0%} of postings ({r['ci_low']:.0%}-{r['ci_high']:.0%})"
        return f"  {display_name(r['tool']):<{width}}  {status:<7}  {pct:<30}  {_flag(r)}".rstrip()

    lines.append("Missing, ranked by demand:")
    lines += [row(r, "missing") for _, r in rep.missing.iterrows()] or ["  nothing, nice"]
    lines.append("\nAlready on your CV:")
    lines += [row(r, "have") for _, r in rep.have.iterrows()] or ["  none of the top tools"]
    if rep.other_cv_tools:
        lines.append(f"\nAlso on your CV, outside the top {rep.top} for this role: "
                     + ", ".join(f"{display_name(t)} ({sh:.0%})" for t, sh in rep.other_cv_tools))
    return "\n".join(lines)