# SkillRadar: report draft (material for the paper)

> **What this file is:** the findings, numbers, story and plan for the 02830 paper, collected while working.
> It is *material*, not text to paste. The course allows AI as an editor, not a ghost writer (W8 lecture), so we write
> the paper's sentences ourselves from this. Keep it updated as results come in; every number here should point to a file.

*Last updated: Sun 8 Nov 2026 (week 9). Technical work finished and frozen; what remains is the peer trial and the writing. Status of the work itself: [`TODO.md`](TODO.md).*

---

## 0. The rules we write against

| Requirement | Source | Our plan |
|---|---|---|
| ACM SIG two-column template, **max 3 pages** (2 people), references excluded | Playbook | Overleaf, `sigconf`; page budget in §3 |
| Sections: Title (names + student numbers), Introduction, Background, The Prototype, Testing and Results, Discussion, References, Appendix | Report template | Exactly these headings |
| Prototype: reproducible from report + citations; **at least two** of pseudo-code, flow diagram, equations, figures | Report template | Pipeline figure, hybrid pseudo-code, demand/coverage equations, app screenshot |
| Testing and Results: **graphs and/or tables required** | Report template | Method-comparison table, ablation, Goal 2 table, peer-trial chart |
| **≥ 10 academic sources** | Report template | 10 listed in §7 (+ web/dataset citations) |
| Appendix: **contribution statement** (equal split, paper *and* code) and **AI-use statement** with full-responsibility sentence | Report template, W8 | §9, §10 |
| Abstract: written last, one paragraph, ~150 words, no citations, *what we did and what we found* | W8 writing lecture | §4 skeleton |
| Method like a recipe: participants, apparatus, procedure, design | W8 writing lecture | Peer trial write-up |
| Negative results are fine if tested and explained | Playbook ("Testing") | Trends dropped; embedding linking failed; verify-only adds nothing; inside the vocabulary the LLM adds nothing |

## 1. The story in one paragraph

Students applying for internships cannot see which **tools** employers actually ask for, or which of them their CV is
missing. SkillRadar compares the tools named in a CV with the tools named in thousands of real job postings for a
target role, and ranks the missing ones by demand with honest uncertainty. To make that comparison trustworthy we test
three things: that tools are **extracted reliably** from free text (Goal 1), that the **demand ranking is robust**
(Goal 2), and that **students can use and trust the report** (Goal 3). The surprising result of Goal 1 is that a
carefully normalised keyword matcher is already very precise (0.97), but a fixed taxonomy misses about a quarter of the
tools people really write; a pretrained LLM, added as a hybrid on top of the keyword matcher, recovers most of them
without losing precision. On postings, its value is **coverage, not correction**.

## 2. How the story changed (useful for the Introduction's framing and the Discussion)

| When | Plan then | What we found | What we changed |
|---|---|---|---|
| Weeks 1–3 (lightning, premortem) | Track skill *trends* over time; group of 3 | — | — |
| Week 5–6 | Trends from Jan vs Apr 2024 | Both datasets are single snapshots; Jan vs Apr differences were scraper artefacts (SE: 14 of 15 "significant" changes go down) | **No trend claims.** Goal 2 = robust *current* demand (replication across datasets) + entry vs senior |
| Week 6–7 | "Skills" in general | Soft skills / methods are not comparable or matchable reliably | **Skill = a named tool** (O\*NET Hot Technology / In Demand) |
| Week 7–8 | — | Lost a group member | Scope cut, 3-page paper, peer trial 6–8 |
| Week 8 | — | Duplicate ads (4,049 primary / 342 secondary), UX role-pattern bug (31% wrong), Google/Facebook as aliases | Dedup, word-boundary role patterns, MANUAL_DROP from evidence |
| Week 8 | LLM as a *verifier* of keyword matches | — | Hybrid design after Clavié & Soulié |
| Week 9 | — | Keyword precision already 0.97; only 4 false positives in 30 postings; **23% of labelled tools outside our vocabulary** | LLM role shifted from correction to **coverage**; method study judged on recall over *all* tools |
| Week 9 | Embedding linking to O\*NET | Every embedding link on dev was a related but wrong tool | **Linking off** (a reported negative result) |
| Week 9 | — | Pilot feedback: ranges unclear, show matches first, looks generic | Redesign: have-first report, plain-language range key, radar chart |
| Week 9 | Matcher v2: add the LLM's out-of-vocabulary finds to the keyword vocabulary | The list of tools would come from our test misses (leakage), and it would change the app and Goal 2 mid-trial | **Cut → future work**; app and numbers frozen |

The arc to tell: *ambitious idea → data showed what it can and cannot support → narrowed to claims we can test → each
method choice justified by a measured problem.* That is the "select suitable methods" and "test whether goals are
reached" learning objectives, shown rather than claimed.

## 3. Page budget (3 pages)

| Section | Budget | Must contain |
|---|---|---|
| Title + abstract | ~0.25 | Names, student numbers |
| Introduction | ~0.4 | Motivation, 3 goals with tests and targets, delimitation |
| Background | ~0.4 | Skill extraction (SkillSpan, Nguyen), LLM matching (Clavié & Soulié), linking (Zhang 2024), demand from ads (Deming & Kahn), HCAI (Amershi, Bansal) |
| The Prototype | ~0.75 | Pipeline figure, matcher steps, hybrid pseudo-code, demand + coverage equations, app screenshot with HCAI choices |
| Testing and Results | ~0.9 | Labels/agreement, method table, ablation (compact), Goal 2 table, peer trial |
| Discussion | ~0.3 | What the results mean, limitations, future work |

Overflow → appendix: strict-scoring tables, full ablation, rank intervals, entry-vs-senior table, prompts, label guidelines, questionnaire.

## 4. Section by section

### Title (subject + narrowing; W8: "every word tells")
Options to choose from or improve:
- *SkillRadar: Ranking Students' Missing Tools by Job-Posting Demand*
- *SkillRadar: Keyword and LLM Tool Extraction for a CV-to-Job-Market Gap Report*
- *Which Tools Is My CV Missing? Robust Demand Estimates and Hybrid LLM Extraction for Students*

### Abstract (write last; skeleton only)
- What: a web prototype comparing CV tools with demand in ~10,800 LinkedIn postings for five roles
- How tested: blind double-labelled postings (κ 0.90); keyword vs LLM-only vs hybrid on held-out postings; a check on CVs; replication of rankings across two datasets; peer trial
- Found: keyword P 0.97 but finds 73% of all tools; hybrid 95% (+22 points) at the same precision; rankings replicate (ρ 0.80–0.87 for three roles); peer-trial result
- One sentence on what it means

### Introduction
- Motivation: students target internships; LinkedIn's skill match is per posting and paywalled; generic CV checkers are vague. Who cares and why.
- Prototype in one line: upload CV → choose role → check the tools found → ranked missing tools with 95% ranges.
- Goals table (from README) with each test and the target **set before measuring**: Goal 1 P ≥ 0.85, R ≥ 0.75; Goal 2 ρ ≥ 0.8; Goal 3 task success, usefulness, trust, correction rate.
- Delimitation: tools only; no trends; judges the CV text, not the person; LinkedIn 2024, ~85% US; no salary or hiring claims.

### Background (several citations expected)
- Skill extraction as a task, and annotation practice: SkillSpan (Zhang et al. 2022). We restrict to tools.
- LLMs for skill extraction/matching: Nguyen et al. 2024 (LLMs weaker than supervised overall, better on complex mentions); Clavié & Soulié 2023 (candidate generation + LLM re-ranking). Our hybrid follows the latter.
- Linking mentions to a taxonomy is hard: Zhang, van der Goot & Plank 2024 (ESCO linking); embeddings as a linking method (Efficient Text Encoders 2025). O\*NET vs ESCO.
- Job ads as a measure of demand, and their limits: Deming & Kahn 2018; Hershbein & Kahn 2018.
- Human-centred AI: Amershi et al. 2019 (show confidence, support correction, explain why); Bansal et al. 2021 (explanations can raise acceptance of wrong output).

### The Prototype (product, not process; reproducible)
**Figure 1: pipeline** (offline build → app → tests). Draft in FigJam/draw.io: O\*NET → vocabulary (301 tools, 448 aliases) → keyword matcher → posting table → demand; CV → parser → same matcher → user check → report.

**Vocabulary and keyword matcher**: O\*NET tools flagged Hot Technology / In Demand; four normalisation steps (exact → vendor stripping → acronyms that abbreviate the preceding words → case-sensitive short names), MANUAL_DROP decided from 20 real snippets per alias. Same matcher for CVs and postings, so both sides use one vocabulary.

**Demand and coverage (equations):**
- Demand of tool *t* for role *r*: p̂ = k / n, where k = postings for *r* mentioning *t* (once per posting), n = postings for *r* after removing identical ad texts; 95% Wilson interval.
- Coverage of a CV with tools *C* against the top-15 tools *T*: coverage = Σ_{t ∈ C∩T} p̂_t / Σ_{t ∈ T} p̂_t (demand-weighted, so missing a tool in 80% of postings costs more than one in 10%).

**LLM methods (pseudo-code for Hybrid):**
```
candidates ← keyword_matcher(text)                       # with the matched phrase
answer ← LLM(rules, 2 dev examples, text, candidates)   # JSON: keep/reject + quote; additional tools + quote
for c in candidates: keep c unless answer rejects it
for (name, quote) in answer.additional:
    if quote not in text and name not in text: drop     # grounding check
    else: tool ← alias_lookup(name) or "new:" + name    # same lookup as the human labels
return kept candidates ∪ added tools
```
Settings: `gemini-3.5-flash-lite`, temperature 0, JSON schema, few-shot from dev postings only, embedding linking off (chosen on dev), answers cached. LLM-only = the same without candidates. Nothing is trained; two settings were chosen on dev and frozen (`llm-v1-frozen`).

**Human-centred design (Figure 2: app screenshot of the report)**, each choice tied to Amershi et al.:
- user checks and corrects the found tools before any report (support efficient correction)
- each tool shows the CV phrase it came from (make clear why)
- every percentage has a 95% range plus a plain-language key (make clear how well the system can do it)
- tools you have are shown before missing ones (pilot feedback)
- radar: distance from the centre = demand; teal = on CV, amber = missing
- CV held in memory only; the LLM is not used on CVs in the app (privacy)

### Testing and Results
**Goal 1, setup:** 40 data-scientist postings drawn once (seed 42), 10 dev / 30 test; both authors labelled all 40 blind with written guidelines; agreement F1 0.86, Cohen's κ 0.90; gold = union (6.8 tools per posting). Matchers frozen before the test split was scored. Metrics micro-averaged; 95% CIs by bootstrap over postings; differences by paired bootstrap.

**Table 1: method comparison (test, 30 postings)**: from `evaluation/results/goal1_test_lenient.md`

| Method | Precision | Recall (all) | F1 (all) | s / posting |
|---|---|---|---|---|
| Keyword (frozen) | 0.97 (0.95–0.99) | 0.73 (0.64–0.81) | 0.83 | ≈ 0 |
| LLM only | 0.98 (0.97–1.00) | 0.92 (0.88–0.96) | 0.95 | 21.6 |
| Hybrid | 0.97 (0.95–0.99) | 0.95 (0.92–0.97) | 0.96 | 17.7 |
| Hybrid, verify only | 0.98 (0.96–1.00) | 0.73 (0.64–0.81) | 0.83 | 17.7 |

Key sentences to make (in our words):
- Hybrid vs keyword: recall (all) **+0.22 (95% CI +0.15 to +0.29)**; precision −0.00 (−0.02 to +0.02). Out-of-vocabulary misses fell from 47 to 7.
- Verify-only rejected 1 keyword match in 30 postings → keyword false positives are rare on postings; the LLM's value is coverage.
- On in-vocabulary tools all methods are near ceiling (F1 0.96–0.97, differences n.s.).
- All methods meet the pre-set targets; recall over all tools is met only with the LLM.

**Table 2 / Figure 3: keyword ablation** (`goal1_test_ablation.md`, strict): recall (vocab) exact 0.56 → vendor 0.76 → acronym 0.95 → full 0.94; false positives 4 → 7 → 8 → 4. Acronyms are the biggest single gain; the case rules halve the false positives. All vs exact: p < 0.001. A bar chart with CI whiskers works well here.

**Out-of-vocabulary analysis** (47 test misses of the keyword matcher; automatic split, *verify by hand*): ~13 in our vocabulary but unreachable by aliases (Azure ×4: blocked by our own `NO_SHORT` rule; EC2: acronym rule), ~11 in O\*NET but not flagged Hot/In Demand (GCP, BigQuery, Keras), ~23 not in O\*NET at all (Databricks ×3, UiPath, Dask). → the taxonomy, not the matching, limits recall.

**Embedding linking (negative result, dev split):** at threshold 0.80 the linker mapped BigQuery → MySQL, MXNet → PyTorch, Kinesis → Kubernetes, SPARQL → GraphQL, Databricks → Apache Spark. Every threshold that allowed links lowered F1 (all) (LLMOnly 0.93 → 0.75 at 0.70). Semantic similarity groups *related* products, which is the wrong notion of identity for tools. Linking was switched off before the test.

**Scoring note:** lenient scoring credits a found tool outside the vocabulary when its name matches a label (squashed equality or containment, ≥ 4 characters), for all methods alike; keyword numbers are identical under both. Under strict scoring every out-of-vocabulary tool counts as wrong, so LLM precision drops to 0.77–0.78 (39 of LLMOnly's 42 strict false positives are correct new tools). Strict tables in the appendix.

**Goal 1, CVs (a check, not a separate result):** 5 CVs from volunteers with consent (1 dev, 4 test), labelled by both authors (positive agreement F1 0.94; the one real disagreement was five niche tools on one CV), gold = union. Keyword matcher only: the LLM is not run on CVs (privacy; the app does not use it on CVs). From `evaluation/results/goal1_cv_keyword.md`, 4 test CVs, 61 labelled tools:

| Matcher | Precision | Recall (vocab) | Recall (all) |
|---|---|---|---|
| exact | 0.95 | 0.89 | 0.69 |
| full (frozen) | 0.96 (0.88–1.00) | 1.00 | 0.77 (0.69–0.88) |

Key sentence: on CVs the pattern from postings repeats. Precision stays high, and recall is limited by the same share of tools outside the vocabulary (23%, e.g. Databricks, Jupyter, Futhark). n = 4, so this supports the posting result rather than standing alone.

**Parsing robustness (one or two sentences):** the app was tried on 15+ CVs from 5 people, as PDF (standard templates and two-column designs made in Figma) and .docx. No parsing failures; the only tools missed were outside the vocabulary (e.g. Julia, Matplotlib). In two-column PDFs the text of the columns is interleaved, which leaves tool names intact.

**Goal 2** (`analysis/results/goal2_output.txt`):

| Role | Spearman ρ, Jan vs Apr (95% CI) | Target ρ ≥ 0.8 |
|---|---|---|
| Data analyst | 0.87 (0.77–0.93) | met |
| Software engineer | 0.87 (0.84–0.92) | met |
| Data scientist | 0.80 (0.66–0.88) | at the threshold |
| ML engineer | 0.82 (small sample) | met, wide CI |
| UX designer | 0.63 | not met |

- Top 3–7 tools per role have stable bootstrap rank intervals; below rank ~10 the order is uncertain (→ why the app shows ranges).
- Entry vs senior (BH-corrected): few differences survive; clearest: data-analyst entry ads mention SQL in 36% vs 66% of senior ads.
- Data-quality findings that changed numbers: duplicate ads (earlier DA ρ 0.54 came from duplicates); UX role-pattern bug.

**Goal 3** (`evaluation/user_study.md`, Google Sheet): *pending peer trial.* Report: participants (n, students, own CV or sample), apparatus (hosted app), procedure (think-aloud, 4 tasks, questionnaire), measures (task success, Likert ratings → a small bar chart, correction rate = removed/added tools per session, a real-world Goal 1 check). Pilot so far: 2 feedback rows → redesign (mention as iteration).

### Discussion
- Why keyword precision is high and recall limited: tools are mostly named explicitly in postings; the taxonomy, not the method, is the bottleneck. Matches Nguyen et al.'s point that LLMs help where fixed approaches have no answer.
- Hybrid vs LLM-only: similar results; the hybrid keeps the explainable keyword evidence for the tools it shares with the keyword matcher.
- What the LLM result means, stated precisely: inside the O\*NET vocabulary the LLM adds nothing measurable (ΔF1 +0.01, n.s.), and as a checker of keyword matches it adds nothing (1 rejection in 30 postings). Its whole gain is tools the taxonomy lacks. So the answer to "does the LLM help?" is: not with matching, only with coverage.
- Cost: ~20 s and ~3,400 tokens per posting → infeasible for 1.3 M postings; the app keeps keywords for market data. The cheaper route is to use the LLM's findings to **extend the vocabulary** and keep keyword matching. We did not do this within the project: the tools to add would be chosen from our own test misses, so an honest evaluation needs newly labelled postings, and changing the vocabulary would have changed the app during the peer trial. → future work.
- HCAI: the confirm step is the safety net for extraction errors; Bansal et al. warn that evidence phrases may increase acceptance of wrong tools; the correction rate measures this.
- Threats to validity: 30 test postings from one role; gold = union of two labellers; lenient name matching; one LLM at temperature 0, and the model will change (gemini-2.5-flash was retired during the project); US-heavy 2024 data vs Danish users; single snapshots.
- Future work: vocabulary expansion from LLM findings, evaluated on new labelled postings; ESCO for European users; a published trained extractor (JobBERT) as a further baseline; more roles in the evaluation; a time series to study trends.

## 5. Figures and tables to make

| # | What | Built from | Status |
|---|---|---|---|
| Fig 1 | Pipeline diagram (offline build, app, tests) | FigJam / draw.io from §4 | started (FigJam needed a team pick) |
| Fig 2 | App report screenshot, annotated with the HCAI choices | hosted app, example CV | possible now (app is frozen) |
| Fig 3 | Ablation bar chart: recall (vocab) and precision per step, CI whiskers | `goal1_test_ablation.md` | to do |
| Fig 4 | Method comparison: recall (all) per method with CIs (or Table 1 alone if space is short) | `goal1_test_lenient.md` | to do |
| Table 1 | Method comparison | above | ready |
| Table 2 | Goal 2 replication | above | ready |
| Fig 5 | Peer-trial Likert ratings (6 statements) | Google Sheet | after trial (3 of 6–8 done) |
| Table 3 | Goal 1 on CVs (small) | `goal1_cv_keyword.md` | ready |
| Appendix | Strict tables, rank intervals, entry vs senior, prompts, label guidelines, questionnaire, embedding-link examples | repo | later |

## 6. Findings log (each with its source)

1. Label agreement F1 0.86, κ 0.90 on 40 postings: `evaluate.py --agreement`
2. Keyword, test: P 0.97, R(vocab) 0.94, R(all) 0.73: `evaluation/results/goal1_test_ablation.md`
3. Acronym step +0.39 recall; case rules halve false positives: same
4. 23% of labelled test tools outside the vocabulary; 3-way split ~13/11/23: TODO.md (verify by hand)
5. Hybrid R(all) 0.95, +0.22 (0.15–0.29), precision unchanged: `goal1_test_lenient.md`
6. Verify-only: 1 rejection in 30 postings: same (cost table)
7. Embedding linking only hurt on dev; examples above: `tune_llm.py` output, dev `--errors` (4 Nov)
8. Grounding check first dropped real tools (Stan, H2O, Azure, Kinesis) whose quotes were inexact → relaxed to "quote or name in text" (dev finding, before freezing)
9. LLM cost ~18–22 s, ~3.4k input tokens per posting: cost tables
10. Goal 2 ρ values, rank stability, SQL entry vs senior: `analysis/results/`
11. Duplicates, UX bug, Google/Facebook drops: README "Results so far"
12. Jan vs Apr differences are scraper artefacts: `preprocessing/data_inspection_primary.ipynb` §5
13. Pilot feedback (2 rows) → redesign: Google Sheet, commit 22f0a24
14. Lenient scoring hand-checked: 79 credited pairs, 78 identical names, 1 containment (Amazon Web Services ↔ AWS, correct): `goal1_lenient_pairs.md`
15. CVs: keyword P 0.96, R(vocab) 1.00, R(all) 0.77 on 4 test CVs; 23% of CV tools outside the vocabulary: `goal1_cv_keyword.md`
16. CV labeller agreement: positive F1 0.94 on 5 CVs: `evaluate.py --agreement evaluation/labels_cv_A.csv evaluation/labels_cv_B.csv`
17. Parsing: 15+ CVs from 5 people (PDF incl. two-column Figma designs, .docx), no parsing failures; misses were out-of-vocabulary tools (Julia, Matplotlib): manual test, 8 Nov
18. Matcher v2 cut (leakage + mid-trial change): TODO.md, decisions 8 Nov

## 7. References (≥ 10 academic) and where each is used

1. Zhang, Jensen, Sonniks, Plank 2022. SkillSpan. NAACL. *(Background: task, annotation)*
2. Nguyen, Zhang, Montariol, Bosselut 2024. Rethinking Skill Extraction in the Job Market Domain using LLMs. NLP4HR. *(Background, Discussion)*
3. Clavié & Soulié 2023. LLMs as Batteries-Included Zero-Shot ESCO Skills Matchers. RecSysHR / arXiv 2307.03539. *(Prototype: hybrid design)*
4. Zhang, van der Goot, Plank 2024. Entity Linking in the Job Market Domain. *(Discussion: linking)*
5. NLP for Human Resources: A Survey, 2024, arXiv 2410.16498. *(Background framing)*
6. Efficient Text Encoders for Labor Market Analysis, 2025, arXiv 2505.24640. *(Embeddings for linking)*
7. Amershi et al. 2019. Guidelines for Human-AI Interaction. CHI. *(Prototype HCAI)*
8. Bansal et al. 2021. Does the Whole Exceed its Parts? CHI. *(Discussion: trust)*
9. Deming & Kahn 2018. Skill Requirements across Firms and Labor Markets. J. Labor Economics. *(Demand from ads)*
10. Hershbein & Kahn 2018. Do Recessions Accelerate Routine-Biased Technological Change? AER. *(Representativeness)*
11. (optional) Decorte et al. 2023. Extreme Multi-Label Skill Extraction Training using LLMs. arXiv 2307.10778. *(Road not taken)*
12. (optional) Wilson 1927 (score interval) / MacKenzie 2013 (HCI writing). *(Method)*

Web/data: O\*NET 31.0 (CC BY 4.0), the two Kaggle LinkedIn datasets (licences to confirm), ESCO, Gemini API, Streamlit.
Use DTU FindIt for BibTeX; format per the W8 checklist (numbered, alphabetical, consistent).

## 8. Before we write: things to check

- [ ] Read the sections we cite in each paper (W8: "cited but not verified"); especially Clavié & Soulié's prompt-format claim and Nguyen et al.'s "complex mentions" finding
- [x] Hand-check the out-of-vocabulary names credited by lenient scoring (all 79 correct; `goal1_lenient_pairs.md`)
- [ ] Hand-check the ~13/11/23 out-of-vocabulary split
- [ ] Kaggle licences (two TODOs in the README)
- [x] CV results (above)
- [ ] Peer-trial numbers, then fill Goal 3 in §4

## 9. Contribution statement (appendix): collect as we go

From the commit history (each of us commits our own work): A (Lucia): matcher, pipeline, Goal 2 analysis, evaluation tooling, LLM methods, app. B (Ditte): user-study protocol, testing app and feedback form, pilot notes, notebook explanations. Both: labelling (two labellers), literature, presentation, report sections (to assign). **Aim for an equal split in the report sections**; write down who wrote which section as soon as it is drafted.

## 10. AI-use statement (appendix): collect as we go

Required per the W8 lecture: tool and model, purpose, a few representative prompts, how the output was used and checked, and the sentence that **we take full responsibility for all content, code, analyses and conclusions**. Two kinds of use to separate clearly:

1. **AI as a component of the system:** Gemini (`gemini-3.5-flash-lite`) as the extractor in the LLM methods; prompts in `skillradar/llm_matcher.py`; outputs cached and evaluated against human labels.
2. **AI as an assistant to us:** Claude (claude.ai) for planning against the course material, literature search leads, code (LLM matcher, evaluation additions, app redesign), test design and reviewing results. Checked by: our own test suite, running everything ourselves, frozen test splits, reading the papers we cite. Representative prompts: e.g. "Go through the repo and course material and tell us where we stand for week 9"; "Is our project technical enough for the learning objectives?"; "Explain what freezing, linking and ablation mean." Also the earlier literature-notes prompt in `notes/literature_notes.md`.

Keep a short log of representative prompts while working; a full list is not required.

## 11. Likely examiner questions (defence prep)

- *Why not train a model?* 40 labelled postings are too few; pretrained models adapted with dev-set choices are the suitable method here (Nguyen et al.; Clavié & Soulié); we compared against a strong frozen baseline instead.
- *Isn't lenient scoring flattering?* It applies to every method; keyword numbers are unchanged; strict tables are in the appendix; we hand-checked the credited matches.
- *Why is the gold the union of both labellers?* A tool counts if either of us found it in the text; agreement was high (κ 0.90); the union favours recall, which we report.
- *Why does the app not use the LLM?* Cost/latency for market data; privacy for CVs; the keyword matcher is precise and explainable; the confirm step catches its misses.
- *So did the LLM help at all?* Not with matching: inside the vocabulary and as a checker it adds nothing measurable. It helps with coverage: +0.22 recall over all tools, at the same precision, because it finds tools O\*NET lacks.
- *Why not add the LLM's tools to your vocabulary?* That is the obvious next step, but the list would come from our test misses, so testing it on the same postings would be leakage; it needs new labelled postings. And it would have changed the app during the peer trial. → future work.
- *How do you know the demand ranking is real?* It replicates across two independent datasets (ρ 0.80–0.87 for three roles), and the app shows 95% ranges.
- *What would you do with more time?* Vocabulary expansion (evaluated on new postings), ESCO, more roles in Goal 1, a trained extractor baseline, a time series.

## 12. Final presentation (25 Nov): rough outline

Problem (one student, one CV) → demo of the app → the two numbers that matter (0.73 → 0.95 recall; ρ ≥ 0.8) → what students said → what we learned (taxonomy is the bottleneck; LLMs add coverage, not correction) → limitations.
