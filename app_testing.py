"""SkillRadar PARTICIPANT TESTING app: Upload -> Role -> Check -> Report -> Feedback.

Same flow and look as app.py (skillradar/ui.py), plus the user-study feedback form under the report.
Study responses are only saved with consent: to the Google Sheet from Streamlit Secrets when hosted,
otherwise to a local CSV. CV text stays in session memory, never in the study data.
Keep steps 1-4 in sync with app.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from skillradar import ui
from skillradar.cv_parser import read_cv_bytes
from skillradar.demand import PROCESSED, ROLE_PATTERNS, demand_table, filter_postings, load_posting_tools
from skillradar.matcher import KeywordMatcher
from skillradar.report import STRONG_AT, build_report, display_name, format_report, job_matches
from skillradar.robustness import rank_intervals, replication, seniority
from skillradar.study_logging import save_response, sheet_from_secrets

ONET = Path("data/onet/software_skills.csv")
TOP = 15
SHOW_MISSING = 5          # missing tools shown before 'Show more'
STUDY_STEPS = ["Upload", "Role", "Check", "Report", "Feedback"]

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

st.set_page_config(page_title="SkillRadar User Study", page_icon="📡", layout="wide")
html(ui.CSS)
ss = st.session_state
for k, v in {"step": 1, "cv_text": None, "cv_name": None, "cv_key": None, "role": list(ROLE_PATTERNS)[0],
             "dataset": "all", "kept": {}, "added": [], "study_saved": False}.items():
    ss.setdefault(k, v)

if ss.step > 1 and ss.cv_text is None:          # e.g. after a page reload: start again
    ss.step = 1
html(ui.top_bar(ss.step, STUDY_STEPS))

if not ONET.exists() or get_postings("primary") is None:
    st.error("Data missing. From the repo root run:  `uv run python main.py build --source primary`  "
             "(and `--source secondary`), with the O*NET files in `data/onet/`.")
    st.stop()

matcher = get_matcher()


def set_cv(text: str, name: str, key: str) -> None:
    if ss.cv_key != key:                        # a new CV: forget the previous corrections
        ss.kept, ss.added = {}, []
        ss.study_saved = False
    ss.cv_text, ss.cv_name, ss.cv_key = text, name, key


# ---------------------------------------------------------------------------
# Step 1: Upload
# ---------------------------------------------------------------------------

def step_upload() -> None:
    total = sum(n_postings(r, "all") for r in ROLE_PATTERNS)
    left, right = st.columns([1.1, 1], gap="large", vertical_alignment="center")
    with left:
        html(ui.pill("User study: your feedback is only saved if you submit the form at the end"))
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


@st.cache_resource
def _open_sheet(config_json: str):
    """Opening the sheet is slow, so it is cached, keyed on the secrets themselves: edited secrets reopen it."""
    return sheet_from_secrets({"gsheets": json.loads(config_json)})


def get_study_sheet():
    """The Google Sheet from the app's secrets ([gsheets]), or None -> local CSV. See user_testing/README_TESTING.md.
    Secrets are read on every save (not cached), so secrets added after the app started are picked up."""
    try:
        if "gsheets" not in st.secrets:
            return None
        return _open_sheet(json.dumps(dict(st.secrets["gsheets"]), sort_keys=True))
    except FileNotFoundError:                    # no secrets.toml at all (normal when testing locally)
        return None


TASKS = {   # study field -> what the facilitator observed (the tasks read aloud, evaluation/peer_trial_guide.md)
    "task1_upload_role": "Task 1: upload the CV and choose a role",
    "task2_correct_tools": "Task 2: check and correct the tools found",
    "task3_understand_report": "Task 3: explain what the report says",
    "task4_choose_tool": "Task 4: choose a tool to learn and say why",
}
TASK_LABELS = {"no_help": "Without help", "with_help": "With help", "failed": "Not completed"}


def study_feedback(found: set[str], removed: list[str], missing: list[str]) -> None:
    """Study-only app: feedback is always visible, but save requires consent."""
    st.write("")
    html(ui.header("Step 5 of 5: your feedback", "How was it?", "Please fill this in only if you are taking part in the SkillRadar study. "
                   "It takes about two minutes."))
    if ss.study_saved:
        st.success("Your feedback is now saved, thank you for the feedback.")
        if ss.get("study_where") == "csv":   # tell the facilitator; a hosted server's disk is wiped
            st.caption("Saved on this server only, not in the study's Google Sheet "
                       "(no [gsheets] secrets found).")
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
        not_missing = []
        if missing:
            st.write("**The report says these tools are missing from your CV.** "
                     "Select any that are *not* really missing (for example, they are on your CV under another name). "
                     "Leave it empty if you agree with all of them.")
            not_missing = st.multiselect("Not really missing", missing, key="q_not_missing",
                                         placeholder="I agree with all of them")
        st.divider()
        st.markdown("**For the facilitator.** Filled in by the researcher at the end of the session, "
                    "from what they observed. Participants can skip this part.")
        tasks = {key: st.selectbox(label, list(TASK_LABELS), index=None, format_func=TASK_LABELS.get,
                                   placeholder="Choose", key=f"q_{key}")
                 for key, label in TASKS.items()}
        notes = st.text_area("Where did they hesitate or get stuck? (no names, nothing from the CV)",
                             max_chars=1000, key="q_facilitator_notes")
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
                    where = save_response({
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
                        "missing_shown": len(missing),
                        "missing_agreed": len(missing) - len(not_missing),
                        **{key: value or "" for key, value in tasks.items()},
                        "facilitator_notes": notes,
                    }, sheet=get_study_sheet())
                except Exception as err:            # disk full, sheet not shared, no internet, ...
                    st.error(f"Could not save your feedback ({type(err).__name__}). Please tell the study facilitator.")
                else:
                    ss.study_saved, ss.study_where = True, where
                    st.rerun()                        # hide the form; the thank-you message is shown above


# ---------------------------------------------------------------------------
# Step 4: Report
# ---------------------------------------------------------------------------

def match_all_roles(cv_tools: set[str]):
    _, _, source, levels = DATASETS[ss.dataset]
    pt = get_postings(source)
    return job_matches(cv_tools, {r: demand_table(pt, r, levels=levels) for r in ROLE_PATTERNS},
                       top=TOP, min_share=0.05)


def overview_title(matches) -> str:
    """The page's main answer: which roles the CV's tools fit."""
    strong = [ROLE_NAMES.get(m.role, m.role) for m in matches if m.verdict == "Strong match"]
    if strong:
        names = strong[0] if len(strong) == 1 else ", ".join(strong[:-1]) + " and " + strong[-1]
        return f"Your CV is a strong match for {names}"
    return f"Your closest match is {ROLE_NAMES.get(matches[0].role, matches[0].role)}" if matches else "Your report"


def role_overview(matches) -> None:
    """All roles, best match first. 'View' switches the report below to that role (no details repeated here)."""
    html(ui.section_title("How your CV matches each role",
                          f"Each bar is the share of what postings for that role ask for that is already on your CV, "
                          f"weighted by how often they ask for it. The mark is {STRONG_AT:.0%}: from there we call it a "
                          f"strong match. It describes your tools, not your chances of being hired."))
    for m in matches:
        name = ROLE_NAMES.get(m.role, m.role.capitalize())
        chosen = m.role == ss.role
        row, btn = st.columns([1, 0.13], vertical_alignment="center", gap="small")
        with row:
            html(ui.role_match_row(name, m.have_pct, m.verdict, [display_name(t) for t in m.missing], chosen))
        with btn:
            if chosen:
                html('<div class="sr-shown">Shown below</div>')
            elif st.button("View", key=f"job:{m.role}", use_container_width=True):
                ss.role, ss.w_role = m.role, name
                st.rerun()
    st.write("")


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
    matches = match_all_roles(cv_tools)
    html(ui.header("", overview_title(matches),
                   "First, see how your CV matches each role. Then, below, the full report for one role: "
                   "the tools you already have, and what to learn next, most requested first."))
    role_overview(matches)

    role_name = ROLE_NAMES.get(role, role.capitalize())
    html(ui.subheading(f"{role_name}: you have {len(rep.have)} of the top {k} tools" if len(rep.have)
                       else f"{role_name}: here's where to start",
                       f"Compared with {n:,} {role} postings ({note})."))
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
        html(ui.ci_howto())
        html(ui.section_title("Already on your CV", f"{len(rep.have)} of the top {k} tools for this role. "
                                                     "The number is the tool's rank among the top tools."))
        if rep.have.empty:
            st.caption("None of the top tools yet. The list below is a good place to start.")
        else:
            html("".join(ui.gap_row(rank[r.tool], display_name(r.tool), r.share, r.ci_low, r.ci_high,
                                    tag="Added by you" if r.tool in added else "", have=True)
                         for r in rep.have.itertuples()))
        if rep.other_cv_tools:
            st.caption("Also on your CV, less common for this role: "
                       + ", ".join(f"{display_name(t)} ({s:.0%})" for t, s in rep.other_cv_tools))
        st.write("")
        html(ui.section_title("Missing, most requested first", "The number is the tool's rank among the top tools for this role."))
        if rep.missing.empty:
            st.success("You have all of the top tools for this role.")
        else:
            sen = get_seniority(role)
            rows = []
            for r in rep.missing.itertuples():
                tag, grey = seniority_tag(r.tool, sen)
                rows.append(ui.gap_row(rank[r.tool], display_name(r.tool), r.share, r.ci_low, r.ci_high,
                                       tag=tag if grey else "", grey=grey))
            html("".join(rows[:SHOW_MISSING]))           # the most requested first; the rest on request
            if len(rows) > SHOW_MISSING:
                with st.expander(f"Show the other {len(rows) - SHOW_MISSING} missing tools"):
                    html("".join(rows[SHOW_MISSING:]))

    st.write("")
    f1, f2 = st.columns([3, 2])
    f1.caption("This judges what your CV says, not what you know. Data: LinkedIn 2024, mostly US, so not the Danish market.")
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

    # for the peer trial: what did the user correct? (shown, never stored)
    with st.expander("For the test facilitator"):
        removed = sorted(display_name(t) for t in found if not ss.kept.get(t, True))
        st.write(f"Found by SkillRadar: {len(found)} · removed by user: {len(removed)} · added by user: {len(ss.added)}")
        if removed:
            st.write("Removed: " + ", ".join(removed))
        if ss.added:
            st.write("Added: " + ", ".join(sorted(ss.added)))
        st.caption("Correction details are shown only for this session; CV content is not saved.")
    study_feedback(found, removed, [display_name(t) for t in rep.missing["tool"]])


# ---------------------------------------------------------------------------

{1: step_upload, 2: step_role, 3: step_check, 4: step_report}[ss.step]()
