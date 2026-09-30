# SkillRadar: status & TODO

*Last updated: week 5 (30 Sep 2026). Next session: week 6 (7 Oct), testing-methods lecture.*

## Current state in one paragraph

The whole pipeline runs end to end: **CV → extract tools → compare with job postings for a role → ranked skill-gap report.** It works on a real CV (cv01) against 1,027 real data-scientist postings, with percentages, confidence ranges and a coverage score. What we do **not** have yet is evidence of how *accurate* it is (only 1 CV, no hand-labelled answers), and Goal 2 ("how demand has shifted") still needs to be redefined because our data has no time series.

## Working status

| Part | Status | Notes |
|---|---|---|
| Data (2 Kaggle datasets + O*NET) |  Working | Inspected in `preprocessing/`, findings tables at the end of each notebook |
| Keyword matcher `skillradar/matcher.py` |  Working | Merged to `main` (PR #1). 301 tools, 450 aliases |
| CV parser `skillradar/cv_parser.py` |  Working | Tested on 1 real PDF. Two-column layouts and .docx CVs not tried on real files yet |
| Demand tables `skillradar/demand.py` |  Working | `build --source primary` done: 1,027 DS postings (notebook said 1,107, the gap = postings without text) |
| Report `skillradar/report.py` + `main.py` |  Working | Git-vanishing bug found on cv01 and fixed |
| Tests |  52 passed, 1 expected fail | `uv run pytest` |
| Notebooks |  Outdated | Still use their own old copy of the matcher (incl. the lowercase label bug) |
| Goal 2 (trend / shift) |  Open | Needs a decision, see below |
| Evaluation (accuracy numbers) |  Not started | Needs hand labels |
| Literature review |  Not started | |
| Web prototype |  Not started | Planned for weeks 6–8 |

## Done today (week 5)

- [DONE] Went through the repo and compared it with the plan in our slides
- [DONE] Moved the keyword matcher out of the notebooks into `skillradar/matcher.py`, merging the two copies that had drifted apart (one auto-dropped aliases like Excel, the other didn't)
- [DONE] Fixed the label-matching bug (lowercased labels meant R, Spark, Scala, Excel, scikit-learn never matched) in `extract_tools_from_labels()`
- [DONE] Added `tests/test_matcher.py`, merged to `main` via PR #1
- [DONE] Removed committed `__pycache__` / `.DS_Store` files and gitignored them, plus `*.pdf` / `*.docx` so no CV gets committed by accident
- [DONE] Built the tracer bullet on branch `cv_pipeline`: `cv_parser.py`, `demand.py`, `report.py`, `main.py` (`build` + `report` commands) with tests
- [DONE] Ran `build --source primary` on the real data
- [DONE] Ran the first real CV (lhl_cv_1.pdf) through the whole pipeline
- [DONE] Found and fixed a bug from that run: common CV tools outside the top 15 (Git) disappeared from the report
- [DONE] Rewrote the README "How do I run the app?" section with copy-paste commands
- [DONE] Set up `data/cvs/` for test CVs (gitignored)

## Plan vs. reality (from our premortem slides)

### But we do not need to follow this plan exactly.

| Slide plan | Status |
|---|---|
| Week 3: check data quality & licensing | Done. Two license TODOs left in the README |
| Week 3: extract skills from our own CVs, "riskiest step, tested first" | Done in week 5 (2 weeks late). 1 of 3 CVs so far |
| Week 4–5: lock the "trending skill" definition | Overdue. The data can't support a trend, and slides/docs still promise "rising or falling" |
| Week 4–5: start literature review | Not started |
| Week 6–8: real matching model + trend metric + taxonomy matching + web prototype | ⏭️ Next. The keyword baseline is ready to build on and compare against |
| Week 9–10: backtest trend predictions vs. naive baseline |  Can't happen as planned (no time series). Needs a replacement test, depends on the Goal 2 decision |
| Week 9–10: keyword-vs-taxonomy study |  Needs a hand-labelled evaluation set first |
| Week 11–13: peer trial, report, presentation |  Later. GDPR rules for CVs already sketched (see README) |

### Goals: what's shown vs. what's still unproven

| Goal | Shown | Not proven yet |
|---|---|---|
| 1. Extract CV skills, match to a taxonomy | Works end to end with O*NET as taxonomy | Accuracy (precision/recall) on CVs **and** on postings |
| 2. In-demand skills now + how demand shifted | "Now" works: % of postings with confidence ranges | "Shifted": not possible with our data, goal must be reworded |
| 3. Personal recommendation with evidence | Works: ranked gaps, %, O*NET flags, coverage | Trend direction (depends on Goal 2), usefulness (peer trial) |

## Next steps (in priority order)

### Before week 6 (7 Oct)

- [DONE] **Merge `cv_pipeline` into `main`.** Make sure the fixed `report.py` + `tests/test_report.py` are committed first.
- [ ] **Run all of our CVs** (`cv01`–`cv03`) with `--explain`. For each, write down *before looking at the output* which tools the CV really contains. 
- [ ] **Start `evaluation/cv_labels.csv`**: `cv_id, true_tools, found_by_matcher, false_positives, missed` (no names or contact details).
- [ ] **Decide Goal 2** (see "Open decisions") and update the goal wording in `draft_notes/project_draft.md`, the README and the slides so everything promises the same thing.
- [ ] **Prepare questions for the testing lecture:** how to evaluate the matcher (labelled set size?), what replaces the backtest, how to run the peer trial. 

### Weeks 6–8

- [ ] **Hand-label 30–50 data-scientist postings** (tools actually required) → precision/recall of the matcher on the posting side. This is also the ground truth for the keyword-vs-taxonomy study. *Who:*
- [ ] **Update the notebooks** to `from skillradar.matcher import KeywordMatcher`, switch the label side to `m.extract_tools_from_labels(...)`, rerun Section 4 of `data_inspection_primary.ipynb` and update its findings table. *Who:*
- [ ] **Run `m.suggest_drops(...)`**, decide on `MANUAL_DROP` (start with "Google"), then rebuild both datasets. *Who:*
- [ ] **Goal 2 analysis** in a new notebook, using `data/processed/posting_tools_*.csv` (no need to touch the raw data again). *Who:*
- [ ] **Literature review**: SkillSpan (ITU Copenhagen), JobBERT, ESCO/O*NET-based skill normalisation, labour-market analytics. *Who:*
- [ ] **Taxonomy / synonym matcher**: same `extract_tools(text)` interface as `KeywordMatcher`, so the comparison is a one-line swap. *Who:*
- [ ] **Web prototype**: CV upload + role dropdown → the same report. *Who:*

## Needs refinement

### Matcher (found on lhl_cv_1.pdf)

- [ ] **"bash" missed**: "Bash" is in `CASE_SENSITIVE`, CV writes it lowercase. Decide: remove it from the list, or allow lowercase for tool names that aren't common English words
- [ ] **Jupyter, ChatGPT missed**: in O*NET but not flagged Hot Technology / In Demand, so outside our vocabulary. Decide whether to widen the vocabulary (more recall, more noise)
- [ ] **Claude, Conda, uv missed**: not in O*NET at all. Candidate fix: a data-driven fallback taxonomy from the primary dataset's `job_skills.csv` labels (already in our premortem as the backup plan)
- [ ] **"Google" at 9% of DS postings** is probably the company name, not a tool. Check a few postings, then likely `MANUAL_DROP`
- [ ] **"Go further" matches Go**: capitalised English word at sentence start (known, `xfail` test in `tests/test_matcher.py`)
- [ ] Every fix: add a test case first, then fix, then **rebuild**

### Report

- [ ] **O*NET flag column says "Hot Technology + In Demand" on almost every row** (our vocabulary only contains flagged tools, so it tells us little). Drop it, or use the flags of the role's own O*NET occupation instead
- [ ] Consider showing a short line per report on what the numbers mean (e.g. "based on US-heavy LinkedIn data, Jan 2024")

### CV parser

- [ ] Try two-column PDF CVs and a .docx CV, check `--show-text` for scrambled text

### Data / docs

- [ ] Resolve the two license TODOs in the README before hand-in
- [ ] README logo `skillradar_logo.png` is missing (broken image), add it or remove the lines? Removed for now, but consider adding.
- [ ] Secondary notebook still refers to `data_inspection.ipynb` (old name)

## Open decisions (need all three of us)

1. **Goal 2 reframe**, pick one (or a combination):
   - *Robust current demand*: % of postings + O*NET flags, tested by whether skill rankings replicate across the two datasets (rank correlation of the top 20, bootstrap confidence intervals). Replaces the backtest directly
   - *Entry-level vs. senior*: which skills become more important with seniority (secondary dataset has both)
   - *External time series* for the trend signal only (past O*NET releases, Stack Overflow survey), only if it turns out usable
2. **Single job-ad mode?** `report cv.pdf "ml engineer" --job ad.txt`: for each tool the ad asks for, show whether you have it and how common it is across the role. Matches the C++ example on our slides; small to build
3. **Default for students**: should reports default to entry-level postings (secondary, smaller) or all levels (primary, bigger)?
4. **Evaluation protocol**: how many CVs and postings to label, and who labels (two people label the same items to check agreement?)

## Known limitations (for the report)

- Both datasets are single snapshots (Jan 2024 and Apr 2024), so no real trends
- Data is ~85% US, our users are DTU students in Denmark
- The primary dataset has no entry-level or internship postings
- The report judges what the CV *says*, not what the person knows (e.g. SQL missing on cv01)
- O*NET lags behind new tools (Claude, uv are not in it)

## How to run (quick reference)

```bash
uv sync && uv run pytest
uv run python main.py build --source secondary
uv run python main.py build --source primary
uv run python main.py report data/cvs/cv01.pdf "data scientist" --explain
```

Full instructions in the README.