"""
SkillRadar web prototype (Goal 3).

    uv run streamlit run app.py

Needs data/onet/software_skills.csv and at least data/processed/posting_tools_primary.csv
(made by `uv run python main.py build --source primary`; also build --source secondary for the
entry-level option and the entry-vs-senior tags).

Four steps: Upload -> Role -> Check -> Report. The report shows what the CV already has first,
then what is missing, with a plain-language key for the 95% ranges (peer-pilot feedback).
Look and feel: skillradar/ui.py and .streamlit/config.toml. This file only holds the flow.

Human-centred design choices (see TODO.md, "Changes in direction"):
  * the user checks and corrects the tools we found BEFORE seeing the report (human in the loop)
  * every found tool shows the CV phrase it came from (explainability)
  * every percentage shows its 95% range, plus a "how sure are we?" note (uncertainty)
  * the CV is only held in memory for this session, never written to disk or logged (privacy)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from skillradar import ui
from skillradar.cv_parser import read_cv_bytes
from skillradar.demand import PROCESSED, ROLE_PATTERNS, demand_table, filter_postings, load_posting_tools
from skillradar.matcher import KeywordMatcher
from skillradar.report import build_report, display_name, format_report
from skillradar.robustness import rank_intervals, replication, seniority

ONET = Path("data/onet/software_skills.csv")
TOP = 15

# key -> (title, description, source, levels)
DATASETS = {
    "all": ("All experience levels", "LinkedIn, Jan 2024 · US, UK, Canada, Australia · largest sample", "primary", None),
    "entry": ("Entry level & internships", "LinkedIn, Apr 2024 · US only · closest to student roles", "secondary",
              ["entry", "internship"]),
}

ROLE_NAMES = {"data scientist": "Data scientist", "data analyst": "Data analyst",
              "software engineer": "Software engineer", "ml engineer": "ML engineer", "ux designer": "UX designer"}

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
def get_postings(source: str):
    return load_posting_tools(source) if (PROCESSED / f"posting_tools_{source}.csv").exists() else None


@st.cache_resource
def get_replication(role: str):
    a, b = get_postings("primary"), get_postings("secondary")
    if a is None or b is None:
        return None
    return replication(a, b, role, country_a="United States", n_boot=300)


@st.cache_resource
def get_seniority(role: str):
    b = get_postings("secondary")
    if b is None:
        return None
    s = seniority(b, role, top=30)
    return None if s.empty or min(s.attrs["n_junior"], s.attrs["n_senior"]) < 30 else s


@st.cache_resource
def get_stable_ranks(role: str, dataset: str) -> int:
    """How many of the top ranks have a bootstrap rank interval no wider than +-1."""
    _, _, source, levels = DATASETS[dataset]
    ri = rank_intervals(get_postings(source), role, top=15, levels=levels, n_boot=300)
    k = 0
    for lo, hi in zip(ri["rank_lo"], ri["rank_hi"]):
        if hi - lo > 1:
            break
        k += 1
    return k


def html(s: str) -> None:
    st.markdown(s, unsafe_allow_html=True)


def go(step: int) -> None:
    st.session_state.step = step
    st.rerun()


def n_postings(role: str, dataset: str) -> int:
    _, _, source, levels = DATASETS[dataset]
    pt = get_postings(source)
    return 0 if pt is None else len(filter_postings(pt, role, levels))


def seniority_tag(tool: str, sen) -> tuple[str, bool]:
    """Tag for a missing tool: only says something when the entry vs senior difference is significant."""
    if sen is not None:
        row = sen[sen["tool"] == tool]
        if not row.empty and bool(row.iloc[0]["significant"]):
            d = row.iloc[0]["diff_pp"]
            return ("More in senior roles" if d > 0 else "More in entry-level roles"), True
    return "Missing", False


# ---------------------------------------------------------------------------
# State (memory only; disappears when the browser tab is closed)
# ---------------------------------------------------------------------------

st.set_page_config(page_title="SkillRadar", page_icon="📡", layout="wide")
html(ui.CSS)
ss = st.session_state
for k, v in {"step": 1, "cv_text": None, "cv_name": None, "cv_key": None, "role": list(ROLE_PATTERNS)[0],
             "dataset": "all", "kept": {}, "added": []}.items():
    ss.setdefault(k, v)

if ss.step > 1 and ss.cv_text is None:          # e.g. after a page reload: start again
    ss.step = 1
html(ui.top_bar(ss.step))

if not ONET.exists() or get_postings("primary") is None:
    st.error("Data missing. From the repo root run:  `uv run python main.py build --source primary`  "
             "(and `--source secondary`), with the O*NET files in `data/onet/`.")
    st.stop()

matcher = get_matcher()


def set_cv(text: str, name: str, key: str) -> None:
    if ss.cv_key != key:                        # a new CV: forget the previous corrections
        ss.kept, ss.added = {}, []
    ss.cv_text, ss.cv_name, ss.cv_key = text, name, key


# ---------------------------------------------------------------------------
# Step 1: Upload
# ---------------------------------------------------------------------------

def step_upload() -> None:
    total = sum(n_postings(r, "all") for r in ROLE_PATTERNS)
    left, right = st.columns([1.1, 1], gap="large", vertical_alignment="center")
    with left:
        html(ui.pill(f"Built on {total:,} real job postings"))
        html(ui.header("", "Find the tools your CV is missing",
                       "Upload your CV and pick a role. We compare the tools on it with what real job postings "
                       "ask for, and rank what you are missing.", hero=True))
        up = st.file_uploader("Your CV", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")
        st.caption("PDF, DOCX or TXT. Read in memory, never stored.")
        if up is not None:
            try:
                set_cv(read_cv_bytes(up.getvalue(), up.name), up.name, f"upload:{up.name}:{up.size}")
            except ValueError as err:
                st.error(str(err))
        c1, c2 = st.columns(2)
        if c1.button("Continue", type="primary", use_container_width=True,
                     disabled=up is None or ss.cv_text is None):
            go(2)
        if c2.button("Try an example CV", use_container_width=True):
            set_cv(EXAMPLE_CV, "example_cv.txt", "example")
            go(2)
    with right:
        html(ui.radar())
        html('<div class="sr-caption">Example: a data-science CV against 902 postings</div>')
    html(ui.features([
        ("scan", "Reads your CV", "Picks out named tools like Python, SQL and Tableau, and shows the line each one came from."),
        ("check", "You check the list", "Untick what we got wrong and add what we missed. The report only uses your list."),
        ("radar", "Ranks what's missing", "Every missing tool, ranked by how many postings for your role ask for it."),
    ]))


# ---------------------------------------------------------------------------
# Step 2: Role
# ---------------------------------------------------------------------------

def step_role() -> None:
    html(ui.header("", "Which role are you aiming for?",
                   "We compare your CV only with postings for this role."))
    datasets = [k for k, (_, _, src, _) in DATASETS.items() if get_postings(src) is not None]
    # Streamlit forgets a widget's value when its step is not shown, so each widget gets a key
    # that is seeded once from our own state (ss.role / ss.dataset) and copied back after.
    # Sync the dataset choice BEFORE the role captions use it: Streamlit stores a clicked widget's new
    # value before the rerun, but ss.dataset was only copied back after the role cards were drawn,
    # so the posting counts lagged one click behind.
    ds_titles = {DATASETS[k][0]: k for k in datasets}
    ss.setdefault("w_dataset", DATASETS[ss.dataset][0])
    ss.dataset = ds_titles[ss.w_dataset]
    role_names = {ROLE_NAMES.get(r, r.capitalize()): r for r in ROLE_PATTERNS}
    ss.setdefault("w_role", ROLE_NAMES.get(ss.role, ss.role.capitalize()))
    st.radio("Role", list(role_names), key="w_role", horizontal=True, label_visibility="collapsed",
             captions=[f"{n_postings(r, ss.dataset):,} postings" for r in ROLE_PATTERNS])
    ss.role = role_names[ss.w_role]
    st.write("")
    html(ui.section_title("Compare against"))
    st.radio("Compare against", list(ds_titles), key="w_dataset", horizontal=True, label_visibility="collapsed",
             captions=[DATASETS[k][1] for k in datasets])
    ss.dataset = ds_titles[ss.w_dataset]
    st.write("")
    left, right = st.columns([3, 2])
    left.markdown(f'<div class="sr-pill">📄 {ui.e(ss.cv_name or "")} <span class="sr-muted">· read, not stored</span></div>',
                  unsafe_allow_html=True)
    b1, b2 = right.columns(2)
    if b1.button("Back", use_container_width=True):
        go(1)
    if b2.button("Continue", type="primary", use_container_width=True):
        go(3)


# ---------------------------------------------------------------------------
# Step 3: Check the tools (human in the loop)
# ---------------------------------------------------------------------------

def step_check() -> None:
    found = matcher.extract_tools(ss.cv_text)
    evidence = matcher.evidence(ss.cv_text)
    left, right = st.columns([1.8, 1], gap="large")
    with left:
        html(ui.header("", f"We found {len(found)} tools on your CV",
                       "Are they right? Untick anything that's wrong and add anything we missed. "
                       "Your report only uses this list."))
        if not found:
            st.warning("We found no tools from our list in this CV. Add them below, or check that the PDF contains real text.")
        for t in sorted(found, key=lambda t: display_name(t).lower()):
            c1, c2 = st.columns([0.05, 0.95], vertical_alignment="center")
            k = f"keep:{ss.cv_key}:{t}"
            if k not in ss:
                ss[k] = ss.kept.get(t, True)
            ss.kept[t] = c1.checkbox(display_name(t), key=k, label_visibility="collapsed")
            with c2:
                html(ui.tool_row(display_name(t), evidence.get(t, ""), ss.kept[t]))
        name_to_tool = {display_name(t): t for t in matcher.vocab}
        options = sorted(set(name_to_tool) - {display_name(t) for t in found}, key=str.lower)
        k = f"added:{ss.cv_key}"
        if k not in ss:
            ss[k] = [a for a in ss.added if a in options]
        ss.added = st.multiselect("Add a tool we missed", options, key=k,
                                  placeholder="Search 300 tools, e.g. Tableau, Docker, Power BI…")
    with right:
        st.write(""); st.write("")
        removed = sum(1 for t in found if not ss.kept.get(t, True))
        html(ui.card("You know your CV best",
                     "SkillRadar reads your CV automatically and can be wrong: “Go” can be a programming language "
                     "or just a word. Check the list before we build your report.",
                     strong=True, extra_html=ui.stats([(len(found), "found", False), (removed, "removed", "amber"),
                                                     (len(ss.added), "added", "teal")])))
        st.write("")
        html(ui.card("What counts as a tool?",
                     "Named tools and technologies, like Python, SQL or Tableau. General skills such as machine "
                     "learning or teamwork are not counted."))
        st.write("")
        b1, b2 = st.columns([1, 2])
        if b1.button("Back", use_container_width=True):
            go(2)
        if b2.button("Build my report", type="primary", use_container_width=True):
            go(4)


# ---------------------------------------------------------------------------
# Step 4: Report
# ---------------------------------------------------------------------------

def step_report() -> None:
    title, desc, source, levels = DATASETS[ss.dataset]
    role = ss.role
    found = matcher.extract_tools(ss.cv_text)
    name_to_tool = {display_name(t): t for t in matcher.vocab}
    added = {name_to_tool[a] for a in ss.added if a in name_to_tool}
    cv_tools = {t for t in found if ss.kept.get(t, True)} | added

    demand = demand_table(get_postings(source), role, levels=levels)
    n = demand.attrs["n_postings"]
    note = f"{desc.split(' · ')[0]}, {title.lower()}"
    if n == 0:
        html(ui.header("", "No postings to compare with"))
        st.warning("There are no postings for this role in this dataset. Go back and pick the other dataset.")
        if st.button("Back"):
            go(2)
        return
    rep = build_report(cv_tools, demand, top=TOP, min_share=0.05, note=note)
    top_tools = pd.concat([rep.have.assign(on_cv=True), rep.missing.assign(on_cv=False)]) \
        .sort_values("share", ascending=False).reset_index(drop=True)
    rank = {t: i for i, t in enumerate(top_tools["tool"], start=1)}
    k = len(top_tools)
    title_txt = (f"You already have {len(rep.have)} of the top {k} tools" if len(rep.have)
                 else "Here's where to start")
    html(ui.header("", title_txt, f"Compared with {n:,} {role} postings ({note})."))
    if rep.small_sample:
        st.warning(f"Only {n} postings: the percentages are rough, so look at the ranges.")

    left, right = st.columns([1, 1.35], gap="large")
    with left:
        html(ui.radar([(display_name(r.tool), r.share, bool(r.on_cv)) for r in top_tools.itertuples()]))
        st.write("")
        rr = get_replication(role)
        stable = get_stable_ranks(role, ss.dataset)
        sure = f"The top {stable} places in this ranking are stable; further down, the order is less certain."
        if rr is not None and rr.rho == rr.rho:
            sure += f" The ranking holds up in a second, independent dataset (ρ = {rr.rho:.2f})."
        html(f'<div class="sr-card strong">'
             f'{ui.score(rep.coverage, f"of what {role} postings ask for is on your CV")}'
             f'{ui.coverage_meter([(display_name(r.tool), r.share, bool(r.on_cv)) for r in top_tools.itertuples()])}'
             f'<div class="sr-meter-note">Each block is one of the top {k} tools, sized by how often postings ask for it. '
             f'Teal blocks are on your CV.</div>'
             f'<div class="sr-card" style="margin-top:18px;padding:14px 16px"><h4 style="font-size:14px">How sure are we?</h4>'
             f'<p style="font-size:13.5px">{ui.e(sure)}</p></div></div>')
    with right:
        html(ui.section_title("Already on your CV", f"{len(rep.have)} of the top {k} tools for this role"))
        if rep.have.empty:
            st.caption("None of the top tools yet. The list below is a good place to start.")
        else:
            html(ui.chips([(display_name(r.tool), f"{r.share:.0%}" + (" · added by you" if r.tool in added else ""),
                            r.tool in added) for r in rep.have.itertuples()]))
        if rep.other_cv_tools:
            st.caption("Also on your CV, less common for this role: "
                       + ", ".join(f"{display_name(t)} ({s:.0%})" for t, s in rep.other_cv_tools))
        st.write("")
        html(ui.section_title("Missing, most requested first", "The number is the tool's rank among the top tools for this role."))
        if rep.missing.empty:
            st.success("You have all of the top tools for this role.")
        else:
            html(ui.ci_howto())
            sen = get_seniority(role)
            rows = []
            for r in rep.missing.itertuples():
                tag, grey = seniority_tag(r.tool, sen)
                rows.append(ui.gap_row(rank[r.tool], display_name(r.tool), r.share, r.ci_low, r.ci_high,
                                       tag=tag if grey else "", grey=grey))
            html("".join(rows))

    st.write("")
    f1, f2 = st.columns([3, 2])
    f1.caption("This judges what your CV says, not what you know. Data: LinkedIn 2024, mostly US, so not the Danish market.")
    b1, b2, b3 = f2.columns(3)
    if b1.button("Back", use_container_width=True):
        go(3)
    if b2.button("Start over", use_container_width=True):
        for k in [k for k in ss if str(k).startswith(("keep:", "added:"))]:
            del ss[k]
        for k in ("cv_text", "cv_name", "cv_key"):
            ss[k] = None
        ss.kept, ss.added = {}, []
        go(1)
    b3.download_button("Download", format_report(rep), file_name=f"skillradar_{role.replace(' ', '_')}.txt",
                       type="primary", use_container_width=True)

    # for the peer trial: what did the user correct? (shown, never stored)
    with st.expander("For the test facilitator"):
        removed = sorted(display_name(t) for t in found if not ss.kept.get(t, True))
        st.write(f"Found by SkillRadar: {len(found)} · removed by user: {len(removed)} · added by user: {len(ss.added)}")
        if removed:
            st.write("Removed: " + ", ".join(removed))
        if ss.added:
            st.write("Added: " + ", ".join(sorted(ss.added)))
        st.caption("Write these numbers in the session notes. Nothing here is saved by the app.")


# ---------------------------------------------------------------------------

{1: step_upload, 2: step_role, 3: step_check, 4: step_report}[ss.step]()
