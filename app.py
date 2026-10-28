"""
SkillRadar web prototype (Goal 3).

    uv run streamlit run app.py

Needs data/onet/software_skills.csv and at least data/processed/posting_tools_primary.csv
(made by `uv run python main.py build --source primary`; also build --source secondary for the
entry-level option and the junior/senior column).

Human-centred design choices (see TODO.md, "Changes in direction"):
  * the user checks and corrects the tools we found BEFORE seeing the report (human in the loop)
  * every found tool shows the CV phrase it came from (explainability)
  * every percentage shows its 95% range (uncertainty)
  * the CV is only held in memory for this session, never written to disk or logged (privacy)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from skillradar.cv_parser import read_cv_bytes
from skillradar.demand import PROCESSED, ROLE_PATTERNS, demand_table, load_posting_tools
from skillradar.matcher import KeywordMatcher
from skillradar.report import build_report, display_name
from skillradar.robustness import replication, seniority

ONET = Path("data/onet/software_skills.csv")
TOP = 15

DATASETS = {
    "All experience levels · LinkedIn, Jan 2024 (US, UK, Canada, Australia)": ("primary", None),
    "Entry level & internships · LinkedIn, Apr 2024 (US)": ("secondary", ["entry", "internship"]),
}

EXAMPLE_CV = """Alex Example, MSc student in Human-Centered AI
Projects: built a churn model in Python with pandas and scikit-learn; cleaned survey data in R;
made weekly dashboards in Excel; version control with Git; wrote the thesis in LaTeX.
Courses: machine learning, statistics, databases. Languages: English, Danish."""


# ---------------------------------------------------------------------------
# Cached resources (loaded once per server, shared between users; contain no CV data)
# ---------------------------------------------------------------------------

@st.cache_resource
def get_matcher() -> KeywordMatcher:
    return KeywordMatcher.from_csv(ONET)


@st.cache_resource
def get_postings(source: str) -> pd.DataFrame | None:
    path = PROCESSED / f"posting_tools_{source}.csv"
    return load_posting_tools(source) if path.exists() else None


@st.cache_resource
def get_replication(role: str):
    a, b = get_postings("primary"), get_postings("secondary")
    if a is None or b is None:
        return None
    return replication(a, b, role, country_a="United States", n_boot=300)


@st.cache_resource
def get_seniority(role: str) -> pd.DataFrame | None:
    b = get_postings("secondary")
    if b is None:
        return None
    s = seniority(b, role, top=30)
    return None if s.empty or min(s.attrs["n_junior"], s.attrs["n_senior"]) < 30 else s


def pct_range(lo: float, hi: float) -> str:
    return f"{lo:.0%}–{hi:.0%}"


def junior_senior_note(tool: str, sen: pd.DataFrame | None) -> str:
    if sen is None:
        return ""
    row = sen[sen["tool"] == tool]
    if row.empty:
        return ""
    r = row.iloc[0]
    if not r["significant"]:
        return "similar"
    return f"more in senior roles (+{r['diff_pp']:.0f} pp)" if r["diff_pp"] > 0 else \
           f"more in entry-level roles ({r['diff_pp']:.0f} pp)"


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

st.set_page_config(page_title="SkillRadar", page_icon="📡", layout="centered")
st.title("SkillRadar")
st.write("Upload your CV and pick a role. SkillRadar compares the tools on your CV with what "
         "real job postings for that role ask for, and ranks what you're missing by how often employers ask for it.")

with st.sidebar:
    st.header("About")
    st.markdown(
        "**Skill = a named tool or technology** you can use (Python, SQL, Tableau, Docker). "
        "General skills like *machine learning* or *communication* are not covered.\n\n"
        "**Data:** LinkedIn postings from 2024, mostly US. Not the Danish market, and no trends over time.\n\n"
        "**What we judge:** what your CV *says*, not what you know.\n\n"
        "**Privacy:** your CV is read in memory for this session only. It is not saved or sent anywhere."
    )

if not ONET.exists() or get_postings("primary") is None:
    st.error("Data missing. From the repo root run:  `uv run python main.py build --source primary`  "
             "(and `--source secondary`), with the O*NET files in `data/onet/`.")
    st.stop()

matcher = get_matcher()

# ---- 1. CV ------------------------------------------------------------------
st.subheader("1 · Your CV")
upload = st.file_uploader("PDF, Word (.docx), .txt or .md", type=["pdf", "docx", "txt", "md"])
use_example = st.checkbox("No CV at hand? Use an example CV", value=False)

cv_text, cv_key = None, None
if upload is not None:
    try:
        cv_text, cv_key = read_cv_bytes(upload.getvalue(), upload.name), f"upload:{upload.name}:{upload.size}"
    except ValueError as e:
        st.error(str(e))
elif use_example:
    cv_text, cv_key = EXAMPLE_CV, "example"

# ---- 2. Role ----------------------------------------------------------------
st.subheader("2 · Target role")
col1, col2 = st.columns(2)
role = col1.selectbox("Role", list(ROLE_PATTERNS), format_func=str.capitalize)
options = [k for k, (src, _) in DATASETS.items() if get_postings(src) is not None]
dataset = col2.selectbox("Compare against", options)
source, levels = DATASETS[dataset]

if cv_text is None:
    st.info("Upload a CV (or tick the example) to continue.")
    st.stop()

# ---- 3. Check the tools -----------------------------------------------------
st.subheader("3 · Check the tools we found")
found = matcher.extract_tools(cv_text)
evidence = matcher.evidence(cv_text)

# reset the user's corrections when a different CV is loaded
if st.session_state.get("cv_key") != cv_key:
    st.session_state.cv_key = cv_key
    st.session_state.confirmed = sorted(found, key=display_name)
    st.session_state.added = []

st.caption("Untick anything that is wrong, add anything we missed. The report uses your corrected list.")
if not found:
    st.warning("We found no tools from our list in this CV. Add them below, or check that the PDF contains real text.")

confirmed = st.multiselect(
    "Tools on your CV", options=sorted(found, key=display_name), format_func=display_name,
    key="confirmed",
)
with st.expander("Where did we find them?"):
    for t in sorted(found, key=display_name):
        st.markdown(f"- **{display_name(t)}**: “{evidence.get(t, '')}”")

name_to_tool = {display_name(t): t for t in matcher.vocab}
added = st.multiselect(
    "Add tools we missed", options=sorted(set(name_to_tool) - {display_name(t) for t in found}, key=str.lower),
    key="added",
)
cv_tools = set(confirmed) | {name_to_tool[n] for n in added}

# ---- 4. Report --------------------------------------------------------------
st.subheader("4 · Your skill-gap report")
demand = demand_table(get_postings(source), role, levels=levels)
n = demand.attrs["n_postings"]
if n == 0:
    st.warning("No postings for this role and dataset.")
    st.stop()
rep = build_report(cv_tools, demand, top=TOP, min_share=0.05)
sen = get_seniority(role)

c1, c2 = st.columns(2)
c1.metric(f"Coverage of the top {TOP} tools", f"{rep.coverage:.0%}",
          help="Demand-weighted: missing a tool that is in 80% of postings costs more than one in 10%.")
c2.metric("Postings compared", f"{n:,}")
if rep.small_sample:
    st.warning(f"Only {n} postings: the percentages are rough, look at the ranges.")


def table(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({
        "Tool": df["tool"].map(display_name),
        "In % of postings": df["share"] * 100,
        "95% range": [pct_range(lo, hi) for lo, hi in zip(df["ci_low"], df["ci_high"])],
    })
    if sen is not None:
        out["Entry vs senior"] = df["tool"].map(lambda t: junior_senior_note(t, sen))
    return out


bar = st.column_config.ProgressColumn("In % of postings", format="%.0f%%", min_value=0, max_value=100)
st.markdown("**Missing from your CV, most requested first**")
if rep.missing.empty:
    st.success("You have all of the top tools for this role.")
else:
    st.dataframe(table(rep.missing), hide_index=True, column_config={"In % of postings": bar})

st.markdown("**Already on your CV**")
if rep.have.empty:
    st.write("None of the top tools.")
else:
    st.dataframe(table(rep.have), hide_index=True, column_config={"In % of postings": bar})

if rep.other_cv_tools:
    st.caption(f"Also on your CV, less common for this role: "
               + ", ".join(f"{display_name(t)} ({s:.0%})" for t, s in rep.other_cv_tools))

rr = get_replication(role)
if rr is not None and rr.rho == rr.rho:
    st.caption(f"How stable is this ranking? Between two independent datasets (Jan and Apr 2024, US) the tool "
               f"ranking for {role}s agrees with Spearman ρ = {rr.rho:.2f} (95% CI {rr.ci[0]:.2f}–{rr.ci[1]:.2f}; "
               "1 = identical order).")

# ---- for the peer trial: what did the user correct? (shown, never stored) ----
with st.expander("For the test facilitator"):
    removed = found - set(confirmed)
    st.write(f"Found by SkillRadar: {len(found)} · removed by user: {len(removed)} · added by user: {len(added)}")
    if removed:
        st.write("Removed: " + ", ".join(sorted(map(display_name, removed))))
    if added:
        st.write("Added: " + ", ".join(sorted(added)))
    st.caption("Write these numbers in the session notes. Nothing here is saved by the app.")
