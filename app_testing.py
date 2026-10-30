"""SkillRadar PARTICIPANT TESTING app: Upload -> Role -> Check -> Report -> Survey.

Separate from normal app.py. Study responses are submitted with consent and
saved to a server-local CSV. Do not use ephemeral hosted storage for real trials.
CV text stays in session memory, never in the study CSV.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from skillradar import ui
from skillradar.cv_parser import read_cv_bytes
from skillradar.demand import PROCESSED, ROLE_PATTERNS, demand_table, filter_postings, load_posting_tools
from skillradar.matcher import KeywordMatcher
from skillradar.report import build_report, display_name, format_report
from skillradar.robustness import rank_intervals, replication, seniority
from skillradar.study_logging import save_response, sheet_from_secrets

ONET = Path("data/onet/software_skills.csv")
TOP = 15

DATASETS = {
    "all": ("All experience levels", "LinkedIn, Jan 2024 · US, UK, Canada, Australia · largest sample", "primary", None),
    "entry": ("Entry level & internships", "LinkedIn, Apr 2024 · US only · closest to student roles", "secondary", ["entry", "internship"]),
}
ROLE_NAMES = {"data scientist": "Data scientist", "data analyst": "Data analyst",
              "software engineer": "Software engineer", "ml engineer": "ML engineer", "ux designer": "UX designer"}
EXAMPLE_CV = """Alex Example, MSc student in Human-Centered AI
Projects: built a churn model in Python with pandas and scikit-learn; cleaned survey data in R;
made weekly dashboards in Excel; version control with Git; wrote the thesis in LaTeX.
Courses: machine learning, statistics, databases. Languages: English, Danish."""


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
    if sen is not None:
        row = sen[sen["tool"] == tool]
        if not row.empty and bool(row.iloc[0]["significant"]):
            d = row.iloc[0]["diff_pp"]
            return ("More in senior roles" if d > 0 else "More in entry-level roles"), True
    return "Missing", False


st.set_page_config(page_title="SkillRadar User Study", page_icon="📡", layout="wide")
html(ui.CSS)
ss = st.session_state
for k, v in {"step": 1, "cv_text": None, "cv_name": None, "cv_key": None,
             "role": list(ROLE_PATTERNS)[0], "dataset": "all", "kept": {},
             "added": [], "study_saved": False}.items():
    ss.setdefault(k, v)

if ss.step > 1 and ss.cv_text is None:
    ss.step = 1
html(ui.top_bar(ss.step))

if not ONET.exists() or get_postings("primary") is None:
    st.error("Data missing. From the repo root run: `uv run python main.py build --source primary` "
             "(and `--source secondary`), with the O*NET files in `data/onet/`.")
    st.stop()

matcher = get_matcher()


def set_cv(text: str, name: str, key: str) -> None:
    if ss.cv_key != key:
        ss.kept, ss.added = {}, []
        ss.study_saved = False
    ss.cv_text, ss.cv_name, ss.cv_key = text, name, key


def step_upload() -> None:
    st.info("SkillRadar user study · anonymous feedback is saved only when you submit the final survey with consent.")
    html(ui.radar())
    html(ui.header("", "See which tools stand between you and the job.",
                   "Upload your CV and pick a role. We compare your tools with thousands of real job postings, "
                   "ranked by how often employers ask for them.", hero=True))
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        up = st.file_uploader("Your CV", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")
        st.caption("PDF, DOCX or TXT · read in memory, never stored")
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


def step_role() -> None:
    html(ui.header("Step 2 of 4", "Which role are you aiming for?",
                   "We compare your CV only with postings for this role."))
    datasets = [k for k, (_, _, src, _) in DATASETS.items() if get_postings(src) is not None]
    ds_titles = {DATASETS[k][0]: k for k in datasets}
    ss.setdefault("w_dataset", DATASETS[ss.dataset][0])
    ss.dataset = ds_titles[ss.w_dataset]
    role_names = {ROLE_NAMES.get(r, r.capitalize()): r for r in ROLE_PATTERNS}
    ss.setdefault("w_role", ROLE_NAMES.get(ss.role, ss.role.capitalize()))
    st.radio("Role", list(role_names), key="w_role", horizontal=True, label_visibility="collapsed",
             captions=[f"{n_postings(r, ss.dataset):,} postings" for r in ROLE_PATTERNS])
    ss.role = role_names[ss.w_role]
    st.write("")
    st.markdown("**Compare against**")
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


def step_check() -> None:
    found = matcher.extract_tools(ss.cv_text)
    evidence = matcher.evidence(ss.cv_text)
    left, right = st.columns([1.8, 1], gap="large")
    with left:
        html(ui.header("Step 3 of 4", f"We found {len(found)} tools on your CV.",
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
                     strong=True, extra_html=ui.stats([(len(found), "found", False), (removed, "removed", True),
                                                     (len(ss.added), "added", True)])))
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


@st.cache_resource
def get_study_sheet():
    """The Google Sheet from the app's secrets ([gsheets]), or None -> local CSV. See user_testing/README_TESTING.md."""
    try:
        return sheet_from_secrets(st.secrets)
    except FileNotFoundError:                    # no secrets.toml at all (normal when testing locally)
        return None


def study_feedback(found: set[str], removed: list[str]) -> None:
    """Study-only app: feedback is always visible, but save requires consent."""
    st.divider()
    st.subheader("Step 5 — User-study feedback")
    st.caption("Please complete this only if you are taking part in the SkillRadar study.")
    if ss.study_saved:
        st.success("Your feedback has already been submitted for this session.")
        return
    with st.form("study_feedback"):
        participant_id = st.text_input("Anonymous participant code (given by researcher)", max_chars=30)
        test_run = st.checkbox("Practice submission (not a real participant)")
        st.caption("Rate from 1 (strongly disagree) to 5 (strongly agree).")
        prompts = {
            "accuracy": "SkillRadar correctly identified the tools in my CV.",
            "relevance": "The missing tools seemed relevant to my chosen role.",
            "usefulness": "SkillRadar helped me decide what to learn next.",
            "explanation": "I understood why SkillRadar recommended these tools.",
            "trust": "I trust the information shown in the report.",
            "ease_of_use": "SkillRadar was easy to use.",
        }
        answers = {key: st.selectbox(question, [1, 2, 3, 4, 5], index=None,
                                      placeholder="Choose a rating", key=f"q_{key}")
                   for key, question in prompts.items()}
        st.caption("Please don't include names or anything from your CV.")
        confusion = st.text_area("What was confusing?", max_chars=1000, key="q_confusion")
        improvement = st.text_area("What would you improve?", max_chars=1000, key="q_improvement")
        consent = st.checkbox("I consent to saving my anonymous study results")
        submitted = st.form_submit_button("Save test result", type="primary")
        if submitted:
            if not participant_id.strip():
                st.error("Enter the anonymous participant code provided by the researcher.")
            elif not consent:
                st.error("Consent is required before saving results.")
            elif any(answer is None for answer in answers.values()):
                st.error("Please answer all six questions.")
            else:
                try:
                    save_response({
                        "participant_id": participant_id.strip(),
                        "test_run": test_run,
                        "cv_type": "sample" if ss.cv_key == "example" else "own",
                        "role": ss.role,
                        "dataset": ss.dataset,
                        "detected": len(found),
                        "added": len(ss.added),
                        "removed": len(removed),
                        **answers,
                        "main_confusion": confusion,
                        "suggested_improvement": improvement,
                    }, sheet=get_study_sheet())
                except Exception as err:            # disk full, sheet not shared, no internet, ...
                    st.error(f"Could not save your feedback ({type(err).__name__}). Please tell the study facilitator.")
                else:
                    ss.study_saved = True
                    st.success("Feedback saved. Thank you!")


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
    html(ui.header(f"Your skill-gap report · {role}", "Here's what to learn next.",
                   f"Ranked by how often {n:,} {role} postings ask for each tool · {note}"))
    if n == 0:
        st.warning("No postings for this role and dataset.")
        return
    rep = build_report(cv_tools, demand, top=TOP, min_share=0.05, note=note)
    if rep.small_sample:
        st.warning(f"Only {n} postings: the percentages are rough, look at the ranges.")

    left, right = st.columns([1, 2.6], gap="large")
    with left:
        rr = get_replication(role)
        stable = get_stable_ranks(role, ss.dataset)
        sure = f"The top {stable} positions are stable; further down the order is uncertain."
        if rr is not None and rr.rho == rr.rho:
            sure += f" The ranking replicates across two independent datasets (ρ = {rr.rho:.2f})."
        html(f'<div class="sr-card strong">{ui.ring(rep.coverage)}'
             f'<p class="sr-center">of what {ui.e(role)} postings ask for, weighted by how often each of the top '
             f'{TOP} tools appears</p>'
             f'{ui.stats([(len(rep.have), f"of the top {len(rep.have) + len(rep.missing)} on your CV", False), (len(rep.missing), "missing", True)])}'
             f'<div class="sr-card" style="margin-top:16px;padding:14px 16px"><h4 style="font-size:13px">How sure are we?</h4>'
             f'<p style="font-size:12.5px">{ui.e(sure)}</p></div></div>')
    with right:
        html('<h4 style="margin:4px 0 12px">Missing, most requested first</h4>')
        sen = get_seniority(role)
        if rep.missing.empty:
            st.success("You have all of the top tools for this role.")
        for i, r in enumerate(rep.missing.itertuples(), start=1):
            tag, grey = seniority_tag(r.tool, sen)
            html(ui.gap_row(i, display_name(r.tool), r.share, r.ci_low, r.ci_high, tag=tag, grey=grey))
        html('<h4 style="margin:22px 0 4px">Already on your CV</h4>')
        if rep.have.empty:
            st.caption("None of the top tools.")
        else:
            html(ui.chips([(display_name(r.tool), f"{r.share:.0%}" + (" · added by you" if r.tool in added else ""),
                            r.tool in added) for r in rep.have.itertuples()]))
        if rep.other_cv_tools:
            st.caption("Also on your CV, less common for this role: "
                       + ", ".join(f"{display_name(t)} ({s:.0%})" for t, s in rep.other_cv_tools))

    st.write("")
    f1, f2 = st.columns([3, 2])
    f1.caption("Judges what your CV says, not what you know. Data: LinkedIn 2024, mostly US; not the Danish market.")
    b1, b2, b3 = f2.columns(3)
    if b1.button("Back", use_container_width=True):
        go(3)
    if b2.button("Start over", use_container_width=True):
        for k in [k for k in ss if str(k).startswith(("keep:", "added:", "q_"))]:
            del ss[k]
        for k in ("cv_text", "cv_name", "cv_key"):
            ss[k] = None
        ss.kept, ss.added, ss.study_saved = {}, [], False
        go(1)
    b3.download_button("Download", format_report(rep), file_name=f"skillradar_{role.replace(' ', '_')}.txt",
                       type="primary", use_container_width=True)

    with st.expander("For the test facilitator"):
        removed = sorted(display_name(t) for t in found if not ss.kept.get(t, True))
        st.write(f"Found by SkillRadar: {len(found)} · removed by user: {len(removed)} · added by user: {len(ss.added)}")
        if removed:
            st.write("Removed: " + ", ".join(removed))
        if ss.added:
            st.write("Added: " + ", ".join(sorted(ss.added)))
        st.caption("Correction details are shown only for this session; CV content is not saved.")

    study_feedback(found, removed)


{1: step_upload, 2: step_role, 3: step_check, 4: step_report}[ss.step]()
