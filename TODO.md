# SkillRadar: status & TODO

*Last updated: week 8 (Wed 28 Oct 2026). Next session: week 9 (4 Nov).*
*Final presentation 25 Nov · hand-in 2 Dec (confirm, see Open decisions) · defence 18 Dec.*

## Changes in direction (decided week 8)

1. **We are now 2 people.** Report max **3 pages** (Playbook rule for 2-person groups), a contribution appendix with an equal split, a smaller peer trial, and the cuts listed below.
2. **No trends.** Goal 2 is now *robust current demand* (replication across the two datasets) plus *entry-level vs. senior*. The Jan vs Apr rerun confirms this (see below).
3. **"Skill" = a named tool or technology** (O*NET Hot Technology / In Demand). Said once in the README, the app and the report.
4. **A pretrained model goes on top of the taxonomy, not instead of it.** O*NET stays the vocabulary (*what* we map to). The model decides, in context, whether a piece of text really refers to a tool (*how* we map).
   - Design: the keyword matcher proposes candidates. A pretrained LLM checks each one in context (rejects "Go further", "excel at communication", Google the employer) and may add implicit mentions, but may only answer with O*NET tool names and must quote the evidence.
   - Used on CVs and on the labelled evaluation postings. The 1M+ postings keep the keyword matcher: too many for an LLM, and it already agrees with the dataset's own labels within ~3 points.
   - **Method study (replaces "keyword vs taxonomy"):** keyword vs. LLM-only vs. hybrid, on the same held-out labels.
5. **Human-centred design is now part of the prototype**, not an extra:
   - the user confirms or corrects the extracted tools before the report (human in the loop)
   - every tool shows the CV phrase it came from (explainability)
   - every % shows its uncertainty range
   - CVs stay in memory only; a local model is preferred for privacy (GDPR)
6. **Prototype = web app (Streamlit).** The CLI stays as a developer tool.

## Current state

| Part | Status | Notes |
|---|---|---|
| Data (2 Kaggle + O*NET) | ✅ | Inspected; findings tables need the rerun numbers (task below) |
| Keyword matcher | ✅ | 301 tools, 450 aliases, 0 manual drops. Notebooks now use it (on `cv_pipeline`) |
| CV parser, demand, report, CLI | ✅ | End to end on 1 real CV |
| Tests | ✅ 54 passed, 1 xfail | Verification only (code does what we intended), not accuracy |
| Goals in README | ✅ | On `cv_pipeline`, needs the small updates below |
| Evaluation (labels, P/R) | ❌ | Biggest gap |
| Goal 2 analysis notebook | ❌ | Preview numbers below |
| LLM verifier | ❌ | New |
| Web prototype | ❌ | Blocks peer testing |
| Literature review | ❌ | Reading list below |
| Report (ACM, 3 pages) | ❌ | Start after the 28 Oct writing lecture |
| Trello / work split | ❌ | |

## What the 28 Oct rerun shows

- **Text matcher vs. dataset labels (DS, primary):** 23 of the top 25 tools agree within ~3 points, now including R (49.7 vs 49.5), Spark, Scala and scikit-learn (the label bug is fixed). Exceptions: Power BI (6.8 vs 12.8) and Hadoop (11.1 vs 15.6), where labels are higher, so check those postings. Google is higher from text (9.0 vs 5.9), which suggests the company name, not the tool.
- **Jan vs Apr:** DS has 5 of 20 tools "significant", in mixed directions (noise). SE has 15 of 20, **14 of them down** (a scraper/sample difference, not the market). This confirms: no trend claims.
- **Preview for Goal 2:** Spearman of the top-20 between Jan and Apr is ≈ 0.87 for DS and ≈ 0.71 for SE (rough, from the notebook table). The proper calculation with bootstrap goes in the Goal 2 notebook. SE below 0.8 is a finding to explain, not to hide.
- **Secondary coverage:** 40.3% of all postings have ≥1 tool (was 38.4% with the old matcher). `suggest_drops` flags only Excel (12.4%), a real tool, so keep it. Still suspicious in the top list: Google (138), Facebook (97), C (76), Go (66).

## TODAY (28 Oct): catch-up

- [ ] **A:** Open a PR `cv_pipeline` → `main` and merge it.
- [ ] **A:** Update both findings tables with the rerun numbers above. Also fix: "v2 is larger with validated skills" → "tool-level skill labels (not validated)"; the decision on the Jan vs Apr row → "No trend claims. Goal 2 = replication + entry vs senior".
- [ ] **A+B: tell the teachers at today's consultation:** a member left, show the new scope and goals, and ask the questions under Open decisions.
- [ ] **A+B: today's peer-testing slot: pilot test with 2 classmates.**
  - Show a report (CLI output on their CV, or a printed example) and think aloud: "What would you learn next, and why? What is unclear?"
  - Notes go in `evaluation/pilot_notes.md`.
  - Ask for CVs for the evaluation set: consent, neutral filenames, delete after the project.
- [ ] **A: freeze the matcher.**
  - Spot-check 10 postings each for Google, Facebook, C and Go → put plain-English or company uses in `MANUAL_DROP`.
  - Add a test case per decision, rebuild both datasets, then `git tag matcher-v1-frozen`.
  - The evaluation uses exactly this version.
- [ ] **A: create `evaluation/`.**
  - `sample_postings.py`: 40 data-scientist postings, seed 42, split 10 dev / 30 test, writes the text only (no matcher output).
  - `labels.csv`: `item_id, split, labeller, true_tools`.
  - Label the 10 dev postings blind.
- [ ] **B: Streamlit skeleton `app.py`:** upload CV → role dropdown → `read_cv` → `extract_tools` → `build_report` → table.
- [ ] **A+B:** Trello board (To Do / Doing / Done / Stuck) built from this file, with a name on every card.
- [ ] **A+B:** after the writing lecture, create an Overleaf project with the ACM sigconf template plus the course section template. Paste in the goals.
- [ ] **README:** fix the kappa line (missing "→"); add "A skill = a named tool or technology" to *Not our goals*; add the method comparison to Goal 1's test (keyword vs LLM vs hybrid).

## Plan, weeks 8–13

| Week | Deliverables |
|---|---|
| **8** (→ 4 Nov) | Dev labels done · Goal 2 notebook (Spearman + bootstrap ranks, entry vs mid-senior with multiple-test correction) · Streamlit v0 runs |
| **9** (4 Nov) | `skillradar/llm_matcher.py` (same `extract_tools(text)` interface; prompt = text + candidates + O*NET list; JSON answer with an evidence quote; quotes not found in the CV are rejected automatically) · confirm/correct step + "found in: …" phrases in the app · label the test set, second labeller on 15 items → kappa · pilot the web app with 2 peers |
| **10** (11 Nov) | **Evaluation run:** precision/recall for keyword vs LLM vs hybrid on held-out postings + CVs, plus the ablation of keyword normalisation steps · **peer trial** with 6–8 students (tasks, think-aloud, questionnaire, log of corrections made) · literature section drafted |
| **11** (18 Nov) | Analysis + figures · full report draft · fix the top usability issues from the trial |
| **12** (25 Nov) | Final presentation · report polish |
| **13** (2 Dec) | Hand-in: report PDF, appendices (contributions, questionnaire, prompts, label guidelines), code zip |

Peer-trial measures:
- task success
- perceived accuracy (does each "missing" tool really feel missing?)
- usefulness (Likert)
- trust (would you act on this?)
- **correction rate**: corrections in the confirm step = real-world precision/recall of the extractor. This gives a second evaluation for free.

## Work split (2 people)

- **A (Lucia):** matcher freeze, LLM verifier, evaluation scripts, Goal 2 analysis. Report: method + results.
- **B:** Streamlit prototype, peer trial (protocol, consent text, questionnaire, sessions). Report: introduction, related work, user study.
- **Both:** labelling (two labellers are needed for kappa), literature reading, presentation.
- Everyone's work goes in via **their own commits** (the contribution appendix requires an equal split).

## Literature (read abstract, figures, results; 2–3 lines each in `draft_notes/literature.md`)

| Paper | What we take from it |
|---|---|
| Zhang, Jensen, Sonniks, Plank (2022). *SkillSpan: Hard and Soft Skill Extraction from English Job Postings.* NAACL. | The standard dataset and task definition; domain-adapted BERT models (JobBERT) beat general ones. Our "tools only" scope vs. their hard + soft skills |
| Zhang, van der Goot, Plank (2024). *Entity Linking in the Job Market Domain.* (ITU Copenhagen) | Linking skill mentions to ESCO is hard: best Acc@1 ≈ 24%. Supports our choice of a narrow, explicit tool vocabulary |
| Clavié & Soulié (2023). *Large Language Models as Batteries-Included Zero-Shot ESCO Skills Matchers.* arXiv 2307.03539 | Candidate generation + LLM re-ranking beat the earlier state of the art. **This is our hybrid design** (keyword proposes, LLM verifies) |
| Nguyen, Zhang, Montariol, Bosselut (2024). *Rethinking Skill Extraction in the Job Market Domain using LLMs.* NLP4HR @ EACL | Few-shot LLMs are below supervised models overall but better on complex mentions. Why we use the LLM as a verifier, not as the only extractor |
| *Efficient Text Encoders for Labor Market Analysis* (2025, arXiv 2505.24640) and *NLP for Human Resources: A Survey* (2024, arXiv 2410.16498) | Overview / related-work framing; embedding models as an alternative mapping method |
| One HCAI paper on explanations/trust in recommender or decision-support systems (to find) | Grounds the confirm/correct step, evidence phrases and uncertainty display |

## Course learning objectives → where we cover them

| Objective | Where |
|---|---|
| Extract a concrete goal | 3 goals with tests and targets (README) |
| Collect information / recent methods | Literature table above |
| Select suitable methods | Keyword vs LLM vs hybrid, justified by the literature + our data |
| Scenarios → requirements → design | Student scenario (C++ example) → confirm step, evidence, uncertainty |
| Plan + risk analysis | Premortem, this file, Trello, scope cut after losing a member |
| Larger practical task / lots of code | Package, pipeline, web app |
| Test whether goals are reached | P/R + kappa, Spearman/bootstrap, peer trial |
| Scientific paper | ACM 3 pages |

## Cut / postponed

- Trend/backtest (impossible with our data, reported as a negative finding)
- Fine-tuning a model, a concept/"methods" vocabulary, learning-path stretch goal, single job-ad mode
- External time series (future work only)

## Open decisions (ask the teachers today)

1. **Hand-in date:** the Playbook says both "2 Dec" and "noon Wednesday the week after the last lecture".
2. **LLM on CVs:** local open model (privacy, weaker) vs. API (stronger, needs consent or anonymised CVs)?
3. **Is 40 postings + ~10 CVs enough for the evaluation?**
4. Default for students: entry-level postings (secondary, smaller) or all levels (primary)?

## Needs refinement (carried over)

- [ ] "bash" lowercase missed (CASE_SENSITIVE) · Jupyter/ChatGPT outside the vocabulary · Claude/Conda/uv not in O*NET
- [ ] "Go further" false positive (xfail test). The LLM verifier should fix it, so check it in the eval
- [ ] O*NET flag column says "Hot Technology + In Demand" on almost every row → drop it from the report
- [ ] Try a two-column PDF and a .docx CV
- [ ] Two licence TODOs in the README · secondary notebook still says "notebooks/" and "data_inspection.ipynb"

## Known limitations (for the report)

- Single snapshots (Jan/Apr 2024), no trends · ~85% US data, our users are in Denmark · no entry-level in the primary dataset
- Tools only, not general skills · judges what the CV says, not what the person knows · O*NET lags behind new tools

## How to run

    uv sync && uv run pytest
    uv run python main.py build --source primary      # and --source secondary
    uv run python main.py report data/cvs/cv01.pdf "data scientist" --explain
    uv run streamlit run app.py                         # once B has built it

## Sources:

- [SkillSpan (NAACL 2022)](https://aclanthology.org/2022.naacl-main.366)
- [Entity Linking in the Job Market Domain](https://ar5iv.labs.arxiv.org/html/2401.17979)
- [LLMs as Batteries-Included Zero-Shot ESCO Skills Matchers](https://arxiv.org/pdf/2307.03539)
- [Rethinking Skill Extraction in the Job Market Domain using LLMs (NLP4HR 2024)](https://aclanthology.org/2024.nlp4hr-1.3)
- [Efficient Text Encoders for Labor Market Analysis](https://arxiv.org/pdf/2505.24640)
- [NLP for Human Resources: A Survey](https://arxiv.org/pdf/2410.16498)