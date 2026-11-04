# SkillRadar: status & TODO

*Last updated: week 9 (Wed 4 Nov 2026). Next session: week 10 (11 Nov).*
*Final presentation 25 Nov · hand-in Wed 2 Dec (noon, confirm) · defence 18 Dec.*
*Findings, story and material for the paper: [`report_draft.md`](report_draft.md).*

## Where we are in one paragraph

Goal 1 on postings and Goal 2 are **done and frozen**; the prototype has been **redesigned after the first pilot feedback**.
On 30 held-out postings, the frozen keyword matcher reaches precision 0.97 and recall 0.94 on tools in our vocabulary,
but finds only 73% of *all* labelled tools, because 23% are missing from O*NET. The LLM methods (Gemini, frozen as
`llm-v1-frozen`) close most of that gap: the hybrid finds 95% of all tools (+0.22, CI +0.15 to +0.29) at unchanged precision.
**Still missing:** CV labels + CV evaluation, the peer trial (6–8 students), matcher v2 for the app, literature reading,
and the report.

## Done in week 9 (4 Nov)

- [x] **Goal 1 keyword evaluation** on the test split: P 0.97 · R(vocab) 0.94 · R(all) 0.73 · ablation table → `evaluation/results/goal1_test_ablation.md`
- [x] **Out-of-vocabulary analysis** of the 47 test misses (rough, to verify by hand): ~13 in our vocabulary but no alias reaches them (Azure ×4, Looker, SPSS), ~11 in O\*NET but not Hot/In Demand (GCP, BigQuery, Keras), ~23 not in O\*NET (Databricks ×3, UiPath, Dask)
- [x] **LLM matchers** (`skillradar/llm_matcher.py`): LLMOnly, Hybrid, HybridVerify; grounding check; linking; few-shot from dev; cached answers; tests with a fake client
- [x] **Dev tuning** (`evaluation/tune_llm.py`): embedding linking off (every link was a related but wrong tool); grounding check relaxed to "quote or name in text" after it dropped real tools
- [x] **Frozen** as `llm-v1-frozen` (settings: `evaluation/llm_frozen_settings.txt`) and **evaluated on the test split** → `evaluation/results/goal1_test_lenient.md` (main) and `goal1_test_strict.md` (appendix)
- [x] **App redesign** after pilot feedback: have-first report, plain-language key for the 95% ranges, radar chart of demand, coverage meter, new look; entry-vs-senior tag only when significant; testing app shows 5 steps
- [x] Retry on rate limits and timeouts; key read from a gitignored `.env`

## Results (for the report)

**Goal 1, postings (30 held-out test postings, lenient scoring; keyword numbers are identical under strict scoring)**

| Method | Precision | Recall (vocab) | Recall (all) | F1 (all) | s / posting |
|---|---|---|---|---|---|
| Keyword `full` (frozen) | 0.97 (0.95–0.99) | 0.94 (0.90–0.98) | 0.73 (0.64–0.81) | 0.83 | ≈ 0 |
| LLM only | 0.98 (0.97–1.00) | 0.96 | 0.92 (0.88–0.96) | 0.95 | 21.6 |
| Hybrid | 0.97 (0.95–0.99) | 0.97 | 0.95 (0.92–0.97) | 0.96 | 17.7 |
| Hybrid, verify only | 0.98 (0.96–1.00) | 0.94 | 0.73 | 0.83 | 17.7 |

- Hybrid − keyword: Δrecall(all) **+0.22 (+0.15 to +0.29)**, Δprecision −0.00 (−0.02 to +0.02), ΔF1(vocab) +0.01 (n.s.)
- Verify-only rejected 1 keyword match in 30 postings → on postings the LLM adds **coverage, not correction**
- Grounding check: 1 tool dropped (hybrid), 1 kept by name; embedding linking: off (dev); LLM answers kept 41–42 tools outside O\*NET
- Strict scoring counts every out-of-vocabulary tool as wrong, so the LLM methods drop to precision 0.77–0.78 there (39 of LLMOnly's 42 strict "false positives" are correct new tools). Report lenient as main, strict in the appendix, and **check the lenient name matches by hand**
- Keyword ablation (strict, vs exact): vendor +0.20 recall(vocab), acronym +0.39, full +0.38 with half the false positives (8 → 4); all p < 0.001
- Labels: two labellers, agreement F1 0.86, κ 0.90; gold = union; 6.8 tools per posting; 23% outside our vocabulary

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

**Goal 3**: two feedback rows in the Google Sheet (ranges unclear; put matched tools first; looks AI-generated) → redesign. Peer trial still to run.

## THIS WEEK (until 11 Nov)

- [ ] **Commit + push** this TODO, `report_draft.md`, the README update and `evaluation/llm_frozen_settings.txt`
- [ ] **Check the lenient matches by hand**: run `evaluate.py ... --lenient --errors` and the strict run, and list which out-of-vocabulary names were credited; any doubtful pair → note it in the report
- [ ] **CV labels**: both of us label 6–10 CVs blind (`GUIDELINES.md`, neutral filenames, consent), `split=test`; agreement on CVs as for postings
- [ ] **Billing** on the Gemini key (paid-tier data terms) before any CV goes through the LLM; set a budget alert
- [ ] **CV evaluation**: the same `evaluate.py` command with the CV rows (keyword + LLM methods, frozen settings)
- [ ] **Recruit** 6–8 students for the peer trial in week 10; book slots
- [ ] **Tell the teachers**: lost member and new scope, results so far, and the open decisions below
- [ ] **Overleaf** ACM sigconf skeleton with the template sections; paste in the two result tables
- [ ] **Delete merged branches** on GitHub (`cv_pipeline`, `skill_labels`, `app_fixes_and_notes`, `app_ui_update`, `llm_matcher`)
- [ ] Practice submission `TEST01` on the hosted testing app → check the row → delete it

## Plan, weeks 10–13

| Week | Deliverables |
|---|---|
| **10** (11 Nov) | Peer trial with 6–8 students · CV evaluation · **matcher v2** from the LLM's findings (frequent out-of-vocabulary tools as aliases, Azure / EC2 / Power BI fixes) → rebuild posting tables → rerun `goal2.py` · literature read and noted |
| **11** (18 Nov) | Peer-trial analysis · figures · full report draft · top usability fixes |
| **12** (25 Nov) | Final presentation · report polish |
| **13** (2 Dec) | Hand-in: report PDF, appendices (contributions, AI statement, questionnaire, prompts, label guidelines, strict tables), code zip |

Matcher v2 rule: v1 stays the reported Goal 1 result. v2 is "after evaluation we fixed …", used by the app and for the Goal 2 rerun.

## Work split (2 people)

- **A (Lucia):** LLM verifier, evaluation runs, Goal 2 write-up. Report: method + results.
- **B:** peer trial (protocol, consent, questionnaire, sessions, analysis), app usability fixes. Report: introduction, related work, user study.
- **Both:** labelling (two labellers needed for agreement), literature, presentation.
- Everyone commits **their own work under their own account** (contribution appendix).

## Literature (read the relevant sections before citing; 2–3 lines each in `notes/literature_notes.md`)

| Paper | Where it goes in the report |
|---|---|
| Clavié & Soulié 2023, LLMs as zero-shot ESCO skill matchers | Background + Prototype: our hybrid (candidates + LLM) follows their design |
| Nguyen et al. 2024, Rethinking skill extraction with LLMs | Background + Discussion: LLMs help where fixed methods fail; our "coverage, not correction" result |
| Zhang et al. 2022, SkillSpan | Background: task definition, annotation and agreement reporting; we do tools only |
| Zhang, van der Goot & Plank 2024, Entity linking in the job market | Discussion: linking to a large taxonomy is hard; our embedding-linking failures |
| NLP for HR survey 2024 · Efficient Text Encoders 2025 | Background framing; embeddings as a linking method |
| Amershi et al. 2019, Guidelines for Human-AI Interaction | Prototype: confirm step, evidence, uncertainty display |
| Bansal et al. 2021, Does the Whole Exceed its Parts? | Discussion: explanations can raise trust in wrong output → our correction-rate measure |
| Deming & Kahn 2018 · Hershbein & Kahn 2018 | Background: job ads as a measure of demand, and their representativeness |
| Decorte et al. 2023, synthetic training data with LLMs | Optional: the "train a model" road we did not take, and why |
| O\*NET 31.0, ESCO, the two Kaggle datasets | Data (web/dataset citations) |

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

## Open decisions (ask the teachers)

1. Hand-in: Wed 2 Dec at noon? (The Playbook gives both "2 Dec" and "noon Wednesday the week after the last lecture".)
2. LLM on CVs: is the paid API with consent fine, or should CVs be anonymised first?
3. Is 30 test postings + 6–10 CVs enough for Goal 1?
4. Lenient vs strict scoring as the main table for open-vocabulary methods (we plan lenient, strict in the appendix).
5. Is ρ = 0.80 with CI 0.66–0.88 for data scientists "met"? (We report the CI and don't move the target.)

## Needs refinement

- [x] App: entry vs senior tag only when significant
- [x] App: O\*NET flag column removed (CLI text report still has it)
- [x] Testing app: step indicator shows 5 steps
- [ ] Matcher v2: Azure (blocked by `NO_SHORT`), EC2 (acronym rule misses "Elastic Compute Cloud"), Power BI miss in post_009, GIS false positive
- [ ] "bash" lowercase missed · Jupyter / ChatGPT / uv outside the vocabulary
- [ ] "Go further" false positive (xfail test): the hybrid could reject it in context, but the app uses keywords only
- [ ] Power BI / Hadoop: dataset labels higher than our text matcher. Look at 5 postings each
- [ ] Try a two-column PDF and a .docx CV in the app
- [ ] Two licence TODOs in the README · secondary notebook still says "notebooks/"
- [ ] `evaluation/peer_trial_results.csv`: delete, or keep only for the facilitator's task-success columns
- [ ] `app_testing.py` is a copy of `app.py`: fixes to one must be copied to the other
- [ ] Never rerun `merge_gold.py` (it overwrites manual fixes in `labels_gold.csv`)

## Known limitations (for the report)

- Single snapshots (Jan/Apr 2024), no trends · ~85% US data, our users are in Denmark · no entry level in the primary dataset; small junior samples in the secondary
- Tools only, not general skills · judges what the CV says, not what the person knows · O\*NET lags behind new tools (23% of labelled tools are outside our vocabulary)
- Duplicate removal catches identical ad texts only
- Goal 1: 30 test postings, one role (data scientist), gold = union of two labellers; lenient scoring uses name matching for out-of-vocabulary tools
- LLM: one model at temperature 0, answers cached; model names change quickly (2.5-flash was retired during the project), so the exact model is part of the result
- The app's demand data stays keyword-based: LLM extraction at ~20 s per posting is not feasible for 1.3 M postings

## Sources:
- [SkillSpan (NAACL 2022)](https://aclanthology.org/2022.naacl-main.366)
- [Entity Linking in the Job Market Domain](https://ar5iv.labs.arxiv.org/html/2401.17979)
- [LLMs as Batteries-Included Zero-Shot ESCO Skills Matchers](https://arxiv.org/pdf/2307.03539)
- [Rethinking Skill Extraction in the Job Market Domain using LLMs (NLP4HR 2024)](https://aclanthology.org/2024.nlp4hr-1.3)
- [NLP for Human Resources: A Survey](https://arxiv.org/pdf/2410.16498)
- [Efficient Text Encoders for Labor Market Analysis](https://arxiv.org/pdf/2505.24640)
- [Guidelines for Human-AI Interaction (Microsoft Research)](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/)
- [Bansal et al., Does the Whole Exceed its Parts? (arXiv)](https://arxiv.org/abs/2006.14779)
- [Deming & Kahn, Skill Requirements across Firms and Labor Markets (NBER)](https://www.nber.org/papers/w23328)
- [Hershbein & Kahn, Do Recessions Accelerate Routine-Biased Technological Change? (AER)](https://www.aeaweb.org/doi/10.1257/aer.20161570)

## Summary of sources' relevance (for the report)

| Paper | Relevance | What it can change in your project |
|---|---|---|
| **SkillSpan** (Zhang et al. 2022, ITU Copenhagen) | High | Their **annotation guidelines and agreement reporting** are the model for your labelling. Compare your `GUIDELINES.md` with theirs before you label, and report agreement the way they do. It also positions your scope: they extract hard *and* soft skills, you deliberately do tools only |
| **Clavié & Soulié 2023** (LLMs as zero-shot ESCO matchers) | **Most important** | Directly shapes the LLM verifier: candidate generation plus LLM re-ranking, prompt formats, and their finding that a structured, code-like prompt reduced made-up skills |
| **Nguyen et al. 2024** (Rethinking skill extraction with LLMs) | High | Explains why the LLM should *verify* rather than extract alone (LLMs underperform supervised models overall) and which mention types LLMs handle better. Use it to predict, before running the evaluation, where the hybrid should win |
| **Entity Linking in the Job Market** (Zhang et al. 2024) | Medium | Shows mapping text onto a large taxonomy (ESCO) is hard (≈24% top-1 accuracy). Your argument for a narrow, explicit tool vocabulary |
| **NLP for HR survey** (2024) | Medium | For framing in the introduction or related work; a source of further papers |
| **Efficient Text Encoders** (2025) | Low | Only relevant if you mention embeddings as an alternative method. Could be cut |
| **Amershi et al. 2019, *Guidelines for Human-AI Interaction*** (CHI) | The HCAI design basis | 18 guidelines. Several match your design exactly: "make clear how well the system can do what it can do", "support efficient correction", "make clear why the system did what it did". Use them to **justify** the confirm step, evidence phrases and ranges, and as a checklist for the user study |
| **Bansal et al. 2021, *Does the Whole Exceed its Parts?*** (CHI) | The risk side of explainability | Their study found that AI explanations increased people's acceptance of AI recommendations *whether or not the AI was right*. Your evidence phrases could do the same: users might leave wrong tools unticked because a quote is shown. Your correction-rate measure can test exactly this, which is a strong HCAI point for the paper |
| **Deming & Kahn 2018, *Skill Requirements across Firms and Labor Markets*** (J. of Labor Economics) | Job ads as a measure of skill demand | The established precedent for measuring demand as "% of postings mentioning a skill". It supports your method in Goal 2 |
| **Hershbein & Kahn 2018** (American Economic Review) | Representativeness of posting data | They discuss how well job-ad data represents the actual labour market. That's your duplicate, scraper and US-data limitation, backed by a citation instead of only your own say-so |
| **ESCO** (the EU skills taxonomy) | Your Denmark mismatch | Mention it as the European alternative to O*NET, and as future work for Danish users |
