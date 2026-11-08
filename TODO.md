# SkillRadar: status & TODO

*Last updated: week 9 (Sun 8 Nov 2026). Next session: week 10 (11 Nov).*
*Final presentation 25 Nov · hand-in Wed 2 Dec (noon, confirm) · defence 18 Dec.*
*Findings, story and material for the paper: [`report_draft.md`](report_draft.md).*

## Where we are in one paragraph

**The technical work is finished and frozen.** Goal 1 (postings and CVs) and Goal 2 are evaluated; the app is
redesigned after the pilot, tested on 15+ real CVs (PDF incl. two-column Figma layouts, .docx), hosted, and the peer
trial has started (3 participants in the Google Sheet). On 30 held-out postings the frozen keyword matcher reaches
precision 0.97 but finds only 73% of *all* labelled tools, because 23% are missing from O\*NET; the LLM hybrid finds 95%
(+0.22, CI +0.15 to +0.29) at unchanged precision. On 4 test CVs the same pattern holds (keyword P 0.96, recall over all
tools 0.77, 23% outside the vocabulary). **Decided 8 Nov:** no matcher v2 (future work, see below) and the CV evaluation
stays as it is. **What is left:** finish the peer trial, analyse it, make the figures, write the report and the presentation.

## Decisions taken (8 Nov)

- **No matcher v2.** Extending the vocabulary with the tools the LLM found is the natural next step, but (1) the list
  of tools to add comes from our test-set misses, so scoring v2 on the same test postings would be leakage, and an
  honest test needs newly labelled postings; (2) it would change the posting tables, the Goal 2 numbers and the app
  in the middle of the peer trial. → **Future work** in the report. Evidence for it: the LLM kept 41–42
  out-of-vocabulary tools in 30 postings; Julia and Matplotlib were missed in our own CV tests; peer-trial searches
  for missing tools (if any).
- **CV evaluation stays as it is:** 4 test CVs (+1 dev), keyword matcher only, as a check that the posting result
  carries over to CVs. The LLM is not run on CVs (privacy, and the app does not use it on CVs).
- **App is frozen for the rest of the trial** so every participant sees the same version. Usability findings go in
  the report and the future-work list, not into the app.

## Done in week 9

- [x] **Goal 1 keyword evaluation** on the test split + ablation → `evaluation/results/goal1_test_ablation.md`
- [x] **Out-of-vocabulary analysis** of the 47 test misses (~13 unreachable by our aliases, ~11 in O\*NET but not Hot/In Demand, ~23 not in O\*NET)
- [x] **LLM matchers** (LLMOnly, Hybrid, HybridVerify), dev tuning, frozen as `llm-v1-frozen`, evaluated on test → `goal1_test_lenient.md` (main), `goal1_test_strict.md` (appendix)
- [x] **Lenient matches checked by hand** → `goal1_lenient_pairs.md`: 79 credited pairs, 78 identical names, 1 by containment (Amazon Web Services ↔ AWS, correct)
- [x] **CV labels** (A and B, `labels_cv_A.csv`, `labels_cv_B.csv` → `labels_gold_cv.csv`) and **CV evaluation** (keyword) → `goal1_cv_keyword.md`
- [x] **App redesign** after pilot feedback; role overview with "Strong / Partial / Low match" (no hiring claims); 115 tests pass
- [x] **CV parsing tested** on 15+ CVs from 5 people: PDF (standard templates and two-column Figma designs) and .docx; no parsing failures; the only misses were tools outside the vocabulary (Julia, Matplotlib)
- [x] **Hosted app and feedback sheet** work end to end; 3 peer-trial participants so far

## Results (for the report)

**Goal 1, postings (30 held-out test postings, lenient scoring; keyword numbers are identical under strict scoring)**

| Method | Precision | Recall (vocab) | Recall (all) | F1 (all) | s / posting |
|---|---|---|---|---|---|
| Keyword `full` (frozen) | 0.97 (0.95–0.99) | 0.94 (0.90–0.98) | 0.73 (0.64–0.81) | 0.83 | ≈ 0 |
| LLM only | 0.98 (0.97–1.00) | 0.96 | 0.92 (0.88–0.96) | 0.95 | 21.6 |
| Hybrid | 0.97 (0.95–0.99) | 0.97 | 0.95 (0.92–0.97) | 0.96 | 17.7 |
| Hybrid, verify only | 0.98 (0.96–1.00) | 0.94 | 0.73 | 0.83 | 17.7 |

- Hybrid − keyword: Δrecall(all) **+0.22 (+0.15 to +0.29)**, Δprecision −0.00 (−0.02 to +0.02), ΔF1(vocab) +0.01 (n.s.)
- **How to say it:** inside the O\*NET vocabulary the LLM adds nothing measurable; as a checker it adds nothing (verify-only rejected 1 keyword match in 30 postings). Its gain is finding tools the taxonomy does not contain → **coverage, not correction**
- Grounding check: 1 tool dropped (hybrid), 1 kept by name; embedding linking: off (dev); LLM answers kept 41–42 tools outside O\*NET
- Strict scoring counts every out-of-vocabulary tool as wrong → LLM precision 0.77–0.78 there (39 of LLMOnly's 42 strict "false positives" are correct new tools). Lenient = main, strict = appendix; lenient pairs hand-checked
- Keyword ablation (strict, vs exact): vendor +0.20 recall(vocab), acronym +0.39, full +0.38 with half the false positives (8 → 4); all p < 0.001
- Labels: two labellers, agreement F1 0.86, κ 0.90; gold = union; 6.8 tools per posting; 23% outside our vocabulary

**Goal 1, CVs (4 test CVs, keyword matcher, lenient)** → `evaluation/results/goal1_cv_keyword.md`

| Matcher | Precision | Recall (vocab) | Recall (all) | F1 (all) |
|---|---|---|---|---|
| exact | 0.95 (0.87–1.00) | 0.89 | 0.69 | 0.80 |
| full (frozen) | 0.96 (0.88–1.00) | 1.00 | 0.77 (0.69–0.88) | 0.85 |

- 61 labelled tools, 14 (23%) outside the vocabulary: the same share as on postings
- Labeller agreement on the 5 CVs: positive F1 0.94 (`evaluate.py --agreement`); the only real disagreement is cv02, where A also listed 5 niche tools (Futhark, Cuda, tRPC, Prisma, React); cv05's difference is stray ")" characters in B's file
- Report as a small check, not as a separate result: n = 4 is too small for strong claims

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

**Goal 3**: pilot (2 rows: ranges unclear; put matched tools first; looks AI-generated) → redesign. Peer trial running: 3 participants so far, target 6–8.

## THIS WEEK (week 10, until 15 Nov)

- [ ] **Peer trial:** recruit and run 3–5 more students (target 6–8 in total); same app version, same protocol (`evaluation/user_study.md`)
- [ ] **Note during sessions** whether people search for a tool that is not in the "Add a tool we missed" list (e.g. Julia, Matplotlib) → evidence for the vocabulary-expansion future work
- [ ] **README "Results so far" table:** Goal 1 CVs done (no longer "pending"), peer trial running (3 of 6–8)
- [ ] **Literature:** read the cited sections, 2–3 lines each in `notes/literature_notes.md`
- [ ] **Fig 1 pipeline diagram** (FigJam / draw.io)
- [ ] **Housekeeping:** delete `text.txt` and `job-matches.patch`; cv03 label "BM Spectrum LSF" → "IBM Spectrum LSF"

## Plan, weeks 10–13

| Week | Deliverables |
|---|---|
| **10** (11 Nov) | Peer trial to 6–8 participants · literature notes · Fig 1 · README status update |
| **11** (18 Nov) | Peer-trial analysis (small script: task success, Likert means, correction rate = removed + added tools per session) · Figs 2–5 · **full report draft** |
| **12** (25 Nov) | Final presentation · report polish (abstract last, page budget, references) |
| **13** (2 Dec) | Hand-in: report PDF, appendices (contributions, AI statement, questionnaire, prompts, label guidelines, strict tables), code zip |

No more feature work. Code changes from here on: only the peer-trial analysis script, figure scripts, and real bugs.

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
2. Is 30 test postings + 4 test CVs enough for Goal 1? (We present the CVs as a check, not a separate result.)
3. Lenient vs strict scoring as the main table for open-vocabulary methods (we plan lenient, strict in the appendix).
4. Is ρ = 0.80 with CI 0.66–0.88 for data scientists "met"? (We report the CI and don't move the target.)

## Known issues → report (limitations / future work), not fixes

The app is frozen; these are documented, not changed.

- Vocabulary gaps: Azure (blocked by our own `NO_SHORT` rule), EC2 (acronym rule misses "Elastic Compute Cloud"), Power BI miss in post_009, "bash" in lowercase; Jupyter, ChatGPT, uv, Julia, Matplotlib, Databricks outside the vocabulary
- "Add a tool we missed" only offers the ~300 vocabulary tools, so a participant looking for Julia finds nothing
- GIS false positive; "Go further" false positive (xfail test). The hybrid could reject these in context, but the app uses keywords only
- Power BI / Hadoop: the dataset's own labels are higher than our text matcher
- Two-column PDFs: the parser mixes text from the two columns. Tool names survive and the evidence snippets stay readable, but they can contain words from the other column
- Two licence TODOs in the README · secondary notebook still says "notebooks/"
- `app_testing.py` is a copy of `app.py`: any fix must be made in both
- Never rerun `merge_gold.py` (it overwrites manual fixes in `labels_gold.csv`)

## Known limitations (for the report)

- Single snapshots (Jan/Apr 2024), no trends · ~85% US data, our users are in Denmark · no entry level in the primary dataset; small junior samples in the secondary
- Tools only, not general skills · judges what the CV says, not what the person knows · O\*NET lags behind new tools (23% of labelled tools are outside our vocabulary, on postings and CVs alike)
- Duplicate removal catches identical ad texts only
- Goal 1: 30 test postings, one role (data scientist), gold = union of two labellers; lenient scoring uses name matching for out-of-vocabulary tools; CVs: only 4 test CVs, keyword matcher only
- LLM: one model at temperature 0, answers cached; model names change quickly (2.5-flash was retired during the project), so the exact model is part of the result
- The app's demand data stays keyword-based: LLM extraction at ~20 s per posting is not feasible for 1.3 M postings
- No vocabulary update after the evaluation (no v2): the tools the LLM found are not in the app

## Future work (for the report)

- **Vocabulary expansion from the LLM's findings** (the cut matcher v2): add frequent out-of-vocabulary tools as aliases and fix the alias gaps above, keep the cheap keyword matcher, and evaluate on newly labelled postings (our test misses chose the list, so the old test split cannot score it)
- ESCO for European users · more roles in the Goal 1 evaluation · a published trained extractor (JobBERT) as a further baseline · a time series to study trends

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
