# SkillRadar: status & TODO

*Last updated: week 8 (Wed 28 Oct 2026, after the work session). Next session: week 9 (4 Nov).*
*Final presentation 25 Nov · hand-in 2 Dec (confirm, see Open decisions) · defence 18 Dec.*

## Where we are in one paragraph

The pipeline, the matcher (frozen as `matcher-v1-frozen`), the web prototype and the Goal 2 analysis all work and are on `main`. The test design for all three goals is done (week 6 material), and the blind label sample is drawn. **What is missing is evidence from people:** the labels (Goal 1), the LLM comparison, the user tests (Goal 3), plus the literature review and the report. These are the next three weeks.

## Changes in direction (decided week 8)

1. **We are now 2 people.** Report max **3 pages** (Playbook rule for 2-person groups), a contribution appendix with an equal split, a peer trial with 6–8 people, and the cuts listed below.
2. **No trends.** Both datasets are single snapshots; Jan vs Apr differences are scraper artefacts. Goal 2 = *robust current demand* (replication across datasets) + *entry level vs senior*.
3. **"Skill" = a named tool or technology** (O*NET Hot Technology / In Demand). Said in the README, the app and the report.
4. **A pretrained model goes on top of the taxonomy, not instead of it.** O*NET stays the vocabulary (*what* we map to); the model decides in context whether text really refers to a tool (*how* we map).
   - Hybrid design: the keyword matcher proposes candidates, a pretrained LLM verifies each one in context (rejects "Go further", "excel at communication", company names) and may add implicit mentions. It may only answer with O*NET tool names and must quote the evidence.
   - Used on CVs and the labelled evaluation items. The 1M+ postings keep the keyword matcher.
   - **Method study:** keyword vs LLM-only vs hybrid, on the same held-out labels. This replaces "keyword vs taxonomy".
5. **Human-centred design is part of the prototype:**
   - the user confirms or corrects the found tools before the report (human in the loop)
   - evidence phrases (explainability)
   - 95% ranges (uncertainty)
   - CVs held in memory only (privacy)
6. **Prototype = Streamlit web app.** The CLI stays as a developer tool.

## Current state

| Part | Status | Notes |
|---|---|---|
| Data (2 Kaggle + O*NET) | ✅ | Duplicate ads now removed when loading (primary 4,049, secondary 342) |
| Keyword matcher | ✅ frozen | `matcher-v1-frozen`: 301 tools, 448 aliases, MANUAL_DROP = Google, Facebook |
| Role tagging | ✅ fixed | Word boundaries; before, 31% of "ux designer" postings were building/circuit design |
| CV parser, demand, report, CLI | ✅ | |
| Web prototype `app.py` | ✅ v1 | Confirm/correct step, evidence, ranges, entry vs senior column, facilitator panel. **Not tested with users yet** |
| Goal 1 evaluation setup | ✅ | `evaluation/`: 40 postings (10 dev / 30 test), guidelines, `evaluate.py` (P/R, bootstrap CIs, agreement, ablation) |
| Goal 1 labels | ❌ | **Next task** |
| Goal 2 analysis | ✅ | `analysis/goal2.py`, results below |
| LLM verifier | ❌ | Week 9 |
| User tests (pilot + trial) | ❌ | Pilot this week |
| Literature review | ❌ | Reading list below |
| Report (ACM, 3 pages) | ❌ | Skeleton this week |
| Trello | ❌ | |
| Tests | ✅ 79 passed, 1 xfail | Verification only, not accuracy |

## Course weeks 6–8: what was expected, what we have

| Week | Expected | Status |
|---|---|---|
| 6 · test methods | Test plan tied to the goals (validity, reliability, bias) | ✅ Goals with tests and targets; blind held-out labels; frozen matcher; two labellers; bootstrap CIs; duplicate removal; limitations stated |
| 7 · peer testing | Testable prototype in front of peers | ⚠️ Prototype ready since 28 Oct; no user tests yet |
| 8 · scientific writing + peer testing | Start the paper, keep testing | ❌ Report not started, no pilot yet |

## Results so far (for the report)

**Data quality findings**
- Text matcher vs the dataset's own skill labels (DS): 23 of the top 25 tools within ~3 points. Exceptions: Power BI and Hadoop (labels higher).
- Reposted ads: 4,049 duplicates in primary and 342 in secondary target-role postings. They distorted percentages and the comparisons, so they're now removed.
- UX role pattern bug: "ui" matched inside "Building", "Circuit" etc. 31% of UX postings were wrong. Fixed.
- `MANUAL_DROP` from evidence (`scripts/alias_snippets.py`, 20 snippets per alias): Google 0/20 a tool, Facebook 17/20 social media or company → dropped. C 19/20 and Go 20/20 the language → kept.
- Jan vs Apr: SE had 15 of 20 tools "significant", 14 of them down → scraper difference, not market. No trend claims.

**Goal 2 (after duplicate removal)**

| Role | ρ all levels (95% CI) | ρ levels matched | Target ρ ≥ 0.8 |
|---|---|---|---|
| Data analyst | 0.87 (0.77–0.93) | 0.85 | met |
| Software engineer | 0.87 (0.84–0.92) | 0.84 | met |
| Data scientist | 0.80 (0.66–0.88) | 0.76 | at the threshold, wide CI |
| ML engineer | 0.82 | 0.82 | small sample (n=91 in Apr) |
| UX designer | 0.63 | 0.64 | below; small sparse vocabulary for design tools |

- Rank stability: the top 3–7 tools per role have tight rank intervals; beyond about rank 10 the order is uncertain.
- Entry vs senior (secondary, BH-corrected): few significant differences.
  - Data analyst: SQL 36% junior vs 66% senior.
  - Software engineer: C++ and GitLab more common in junior ads.
  - DS, ML and UX junior groups are too small.
  - Caveat: junior ads list fewer tools (DA 2.9 vs 3.8).
  - Conclusion: for most tools the overall ranking also holds for students.
- The low DA replication seen earlier (0.54) came from duplicate ads, not from level mix.

## THIS WEEK (until 4 Nov)

- [ ] **A+B: labelling (most important).**
  - Each copies `evaluation/labels_TEMPLATE.csv` → `labels_<name>.csv` and follows `evaluation/GUIDELINES.md`.
  - Both label the 10 dev postings + the **same 15 test postings**, independently and without running the matcher.
  - A labels the remaining 15 test postings.
  - `uv run python evaluation/evaluate.py --check evaluation/labels_<name>.csv` → fix typos.
  - `uv run python evaluation/evaluate.py --agreement evaluation/labels_A.csv evaluation/labels_B.csv` → discuss → `labels_gold.csv`.
- [ ] **A+B: pilot the app with 2 classmates** (think-aloud, ~15 min each).
  - Tasks: "upload your CV, check the tools, tell us what you would learn next and why".
  - Notes + the facilitator-panel numbers go in `evaluation/pilot_notes.md` (no names).
  - Ask for CVs for the evaluation set (consent, neutral filenames, delete after the project).
- [ ] **A+B: tell the teachers** about the lost member, the new scope and goals, and ask the Open decisions below.
- [ ] **A+B: Overleaf** with the ACM sigconf template + the course section template. Paste in the goals, the Goal 2 table and the data-quality findings.
- [ ] **A+B: Trello** (To Do / Doing / Done / Stuck) from this file, with a name on every card.
- [ ] **A: update the notebook findings tables** with the 28 Oct rerun numbers. Add the duplicate and UX findings. Fix "v2 is larger with validated skills" → "tool-level labels (not validated)". Jan vs Apr row decision → "No trend claims. Goal 2 = replication + entry vs senior".
- [ ] **A: commit Goal 2 results:** `analysis/results/` + `goal2_output_v2.txt` (move it to `analysis/results/`). Delete the old `goal2_output.txt`.
- [ ] **B: write the peer-trial protocol** in `evaluation/user_study.md`: tasks, think-aloud instructions, consent text, questionnaire (perceived accuracy, usefulness, trust; 5-point Likert), what we log.

## Plan, weeks 9–13

| Week | Deliverables |
|---|---|
| **9** (4 Nov) | **LLM verifier** `skillradar/llm_matcher.py`: same `extract_tools(text)` interface, built as `Class(software_df)`; prompt = text + keyword candidates + O*NET list; JSON answer with an evidence quote; quotes not found in the text are rejected automatically. Plus LLM-only and hybrid variants · gold labels finished · CV labels (≥ 6 test CVs) · fixes from the pilot |
| **10** (11 Nov) | **Goal 1 evaluation run:** `evaluate.py labels_gold.csv --matcher exact vendor acronym full <llm> <hybrid>` on held-out postings + CVs · **peer trial** with 6–8 students · literature section drafted |
| **11** (18 Nov) | Analysis + figures · full report draft · fix the top usability issues |
| **12** (25 Nov) | Final presentation · report polish |
| **13** (2 Dec) | Hand-in: report PDF, appendices (contributions, questionnaire, prompts, label guidelines), code zip |

Peer-trial measures:
- task success without help
- perceived accuracy (does each "missing" tool really feel missing?)
- usefulness and trust (Likert)
- **correction rate** from the facilitator panel: removed tools = false positives, added tools = misses. This gives a second, real-world Goal 1 measurement.

## Work split (2 people)

- **A (Lucia):** LLM verifier, evaluation runs, Goal 2 write-up. Report: method + results.
- **B:** peer trial (protocol, consent, questionnaire, sessions, analysis), app usability fixes. Report: introduction, related work, user study.
- **Both:** labelling (two labellers needed for agreement), literature, presentation.
- Everyone commits **their own work under their own account** (contribution appendix).

## Literature (read abstract, figures, results; 2–3 lines each in `draft_notes/literature.md`)

| Paper | What we take from it |
|---|---|
| Zhang, Jensen, Sonniks, Plank (2022). *SkillSpan: Hard and Soft Skill Extraction from English Job Postings.* NAACL | Standard dataset and task definition; domain-adapted models beat general ones. Our "tools only" scope vs their hard + soft skills |
| Zhang, van der Goot, Plank (2024). *Entity Linking in the Job Market Domain.* | Linking mentions to ESCO is hard (best Acc@1 ≈ 24%). Supports a narrow, explicit tool vocabulary |
| Clavié & Soulié (2023). *Large Language Models as Batteries-Included Zero-Shot ESCO Skills Matchers.* arXiv 2307.03539 | Candidate generation + LLM re-ranking beat the earlier state of the art. **Our hybrid design** |
| Nguyen, Zhang, Montariol, Bosselut (2024). *Rethinking Skill Extraction in the Job Market Domain using LLMs.* NLP4HR | Few-shot LLMs are below supervised models overall but better on complex mentions. Why the LLM verifies rather than extracts alone |
| *Efficient Text Encoders for Labor Market Analysis* (2025, arXiv 2505.24640); *NLP for Human Resources: A Survey* (2024, arXiv 2410.16498) | Related-work framing; embeddings as an alternative mapping method |
| One HCAI paper on explanations / trust / human-in-the-loop correction in decision support (to find) | Grounds the confirm/correct step, evidence phrases and uncertainty display |

## Course learning objectives → where we cover them

| Objective | Where |
|---|---|
| Extract a concrete goal | 3 goals with tests and targets (README) |
| Collect information / recent methods | Literature table |
| Select suitable methods | Keyword vs LLM vs hybrid, justified by the literature and our data |
| Scenarios → requirements → design | Student scenario → confirm step, evidence, uncertainty, privacy |
| Plan + risk analysis | Premortem, this file, Trello, scope cut after losing a member |
| Larger practical task | Package, pipeline, web app, evaluation tooling |
| Test whether goals are reached | P/R + agreement + ablation, Spearman/bootstrap, peer trial |
| Scientific paper | ACM, 3 pages |

## Cut / postponed

- Trends / backtest (impossible with our data; reported as a negative finding)
- Fine-tuning, a concept/"methods" vocabulary, learning-path stretch goal, single job-ad mode
- External time series (future work)

## Open decisions (ask the teachers)

1. **Hand-in date:** the Playbook says both "2 Dec" and "noon Wednesday the week after the last lecture".
2. **LLM on CVs:** local open model (privacy, weaker) vs API (stronger, needs consent or anonymised CVs)?
3. **Is 40 postings + ~6–10 CVs enough** for the evaluation?
4. Default dataset in the app for students: entry level (small, US) or all levels (large)?
5. Is ρ = 0.80 with CI 0.66–0.88 for data scientists "met"? (We report the CI and don't move the target.)

## Needs refinement

- [ ] App: "Entry vs senior" mostly says "similar" → only show it when significant, and hide it for roles with < 30 junior postings
- [ ] App + report: drop the O*NET flag column (it says "Hot Technology + In Demand" on almost every row)
- [ ] "bash" lowercase missed (CASE_SENSITIVE) · Jupyter/ChatGPT outside the vocabulary · Claude/Conda/uv not in O*NET (counted as out-of-vocabulary in the eval)
- [ ] "Go further" false positive (xfail test). Check whether the LLM verifier fixes it
- [ ] Power BI / Hadoop: dataset labels higher than our text matcher. Look at 5 postings each
- [ ] Try a two-column PDF and a .docx CV in the app
- [ ] Two licence TODOs in the README · secondary notebook still says "notebooks/" and "data_inspection.ipynb"

## Known limitations (for the report)

- Single snapshots (Jan/Apr 2024), no trends · ~85% US data, our users are in Denmark · no entry level in the primary dataset; small junior samples in the secondary
- Tools only, not general skills · judges what the CV says, not what the person knows · O*NET lags behind new tools
- Duplicate removal catches identical ad texts only; near-duplicates with edited text may remain

## How to run

    uv sync && uv run pytest
    uv run python main.py build --source primary          # and --source secondary; rebuild after any matcher change
    uv run streamlit run app.py
    uv run python analysis/goal2.py > analysis/results/goal2_output.txt
    uv run python evaluation/evaluate.py --check evaluation/labels_<name>.csv
    uv run python evaluation/evaluate.py evaluation/labels_gold.csv
    uv run python main.py report data/cvs/cv01.pdf "data scientist" --explain

## Sources

- [SkillSpan (NAACL 2022)](https://aclanthology.org/2022.naacl-main.366)
- [Entity Linking in the Job Market Domain](https://ar5iv.labs.arxiv.org/html/2401.17979)
- [LLMs as Batteries-Included Zero-Shot ESCO Skills Matchers](https://arxiv.org/pdf/2307.03539)
- [Rethinking Skill Extraction in the Job Market Domain using LLMs (NLP4HR 2024)](https://aclanthology.org/2024.nlp4hr-1.3)
- [Efficient Text Encoders for Labor Market Analysis](https://arxiv.org/pdf/2505.24640)
- [NLP for Human Resources: A Survey](https://arxiv.org/pdf/2410.16498)