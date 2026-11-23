# SkillRadar
SkillRadar: A CV-to-job-market skill-gap tool for job-seeking students, made in relation to the DTU course: 02830 Advanced Project in Digital Media Engineering

<!-- <p align="center">
  <img src="skillradar_logo.png" width="350" alt="SkillRadar Logo">
</p> -->

## What is this?

Every student that is job-hunting for an internship or first grad role runs into the same wall: it is hard to know in concrete terms, which tools employers are actually asking for, whether your CV reflects that, and which gaps are worth closing before a deadline. LinkedIn's "skill match" needs a paid account and only compares you to one posting at a time. Generic CV checkers give vague advice.

SkillRadar takes your CV and a target role, compares the tools on your CV against real, aggregated job-posting data for that role, and tells you what's missing, how common it is (with a 95% range), and how stable that ranking is.

```
CV → extract tools → you check & correct them → compare with job-posting data for the role → missing tools ranked by demand
```

**Example output** (command-line version, data scientist, primary dataset after duplicate removal, shortened; the coverage figure depends on the CV):
```
SkillRadar: data scientist (902 postings, LinkedIn Jan 2024)
Your CV covers 42% of the demand for the top 15 tools.

Missing, ranked by demand:
  SQL           missing  in 54% of postings (51%-57%)    O*NET Hot Technology + In Demand
  AWS           missing  in 26% of postings (23%-29%)    O*NET Hot Technology + In Demand
  Tableau       missing  in 22% of postings (19%-25%)    O*NET Hot Technology + In Demand

Already on your CV:
  Python        have     in 78% of postings (75%-81%)    O*NET Hot Technology + In Demand
```

> [!NOTE]
> This is a 2-person group project for DTU course 02830, a research prototype, not a consumer product. The matcher, the LLM settings and the app are frozen; the results below are final.

## Our goals

**Aim:** a web prototype where a job-seeking student uploads their CV, picks a target role, and gets a ranked list of the tools they are missing, with evidence from real job postings.

### Goal 1: Extract tools reliably from CVs and job postings
Map free text (CVs and postings) onto one shared vocabulary of tools: the 301 software entries O*NET flags as Hot Technology or In Demand. In this project, a *skill* means a named tool you can use.

**How we test it**

> Hand-label tools in 40 data-scientist postings (10 dev / 30 test, drawn once with seed 42, see `evaluation/manifest.csv`) and 5 CVs (1 dev / 4 test). Report results only on the held-out test items, with the matcher frozen beforehand (`git tag matcher-v1-frozen`).

> Both of us label all 40 postings independently → agreement (F1 between labellers, Cohen's kappa). The gold labels are the union of both label sets (`evaluation/merge_gold.py`): a tool counts if either labeller found it.

> Precision and recall, over tools in our vocabulary and over all labelled tools.

> Ablation: how much each normalisation step adds (exact O*NET names → + vendor stripping → + acronyms → + case rules).

> Method comparison: keyword matcher vs. an LLM alone vs. a hybrid (the keyword matcher proposes candidates, the LLM keeps or rejects them in context and adds missed tools), on the same held-out labels.

> Target (set before measuring): precision ≥ 0.85 and recall ≥ 0.75 on held-out postings.

### Goal 2: Measure current tool demand per role, and show it is robust
For each role, the share of postings that mention each tool, with 95% confidence intervals. Show that this ranking replicates across two independent datasets, and how demand differs between entry-level and senior postings.

**How we test it**

> Rank correlation (Spearman) of the top-20 tools per role between the two datasets (Jan 2024 vs Apr 2024, US postings only). Target: ρ ≥ 0.8 for data scientist, data analyst and software engineer.

> Bootstrap intervals on each tool's rank, to show which positions in the ranking are actually stable.

> Entry-level vs. mid-senior postings within the April dataset: two-proportion tests per tool, Benjamini-Hochberg corrected.

### Goal 3: A prototype students can use and find useful
A web interface: upload CV → choose role → check and correct the tools we found → skill-gap report (missing tools ranked by demand, 95% ranges, coverage score, entry-level vs. senior tag).

**How we test it**

> Pilot with 2 classmates (P01, P02), then a peer trial with job-seeking students using their own CV, with think-aloud on four fixed tasks (choose a role, check the tools, explain the report, name a tool to learn first).

> Task success: can they do each task without help?

> Perceived accuracy: for each "missing" tool, do they agree it is really missing from their CV?

> Six questionnaire statements (1–5): accuracy, relevance, usefulness, understanding, trust, ease of use.

> Correction rate: how many found tools users remove (false positives) or add (misses) in the check step. A second, real-world measurement for Goal 1.

### Not our goals (delimitation)

> **No trends over time.** Both datasets are single snapshots (Jan and Apr 2024). Our January versus April comparison showed differences between the scrapers, not the market, so we make no rising/falling claims.

> **Tools only, not skills in general.** "Machine learning", "statistics" or soft skills are not in our vocabulary. Coverage means coverage of tool demand.

> **The report judges what the CV says,** not what the person knows.

> **Data is LinkedIn 2024, around 85% US.** We do not claim it represents the Danish job market.

> No salary prediction, no application automation, no hiring guarantee. The stretch goals (single job-ad mode, learning suggestions) were not built.

## Results

| Goal | Result |
|---|---|
| 1 · Extraction, postings | **Labels:** 40 postings labelled independently by both of us, agreement F1 = 0.86 (Cohen's κ = 0.90), gold = union. **Keyword matcher** (frozen, 30 held-out postings): precision 0.97, recall 0.94 on tools in our vocabulary, but 0.73 on all labelled tools, because 23% of them are not in our O\*NET vocabulary. **Target met.** Ablation: the acronym step adds the most (+0.39 recall); the case rules halve the false positives (8 → 4). **LLM methods** (frozen, same postings, lenient scoring): the hybrid finds 0.95 of all tools (+0.22, 95% CI +0.15 to +0.29) at unchanged precision (0.97); checking keyword matches in context alone adds nothing (1 rejection in 30 postings). The LLM adds coverage, not correction. Embedding linking hurt on dev and is switched off. Cost: ~18–22 s per posting vs. milliseconds. |
| 1 · Extraction, CVs | 4 held-out CVs, 61 labelled tools (23% outside the vocabulary), keyword matcher only: precision 0.96, recall 1.00 on vocabulary tools, 0.77 on all tools. A small check that the posting result carries over to CVs. |
| 2 · Robust demand | Rankings replicate across the two datasets: Spearman ρ = 0.87 (data analyst), 0.87 (software engineer), 0.80 (data scientist), 0.82 (ML engineer, small sample), 0.63 (UX designer, below target). Matching the experience levels changes ρ by at most 0.04. The top 3–7 tools per role have stable ranks; below about rank 10 the order is uncertain. Few entry vs. senior differences survive correction; the clearest: data-analyst entry ads ask for SQL far less often (36% vs 66%). |
| 3 · Prototype | Pilot (2 classmates) → redesign: tools you have come first, plain-language key for the 95% ranges, radar chart. Peer trial (6 students, P03–P08, own CVs, hosted app): all completed all four tasks, two needed a hint; they kept all 76 tools found, removed none and added one, and agreed that all 44 missing tools shown were really missing. Median ratings: 5 for accuracy, trust and ease of use, 4.5 relevance, 4 understanding, **3 for "helped me decide what to learn next"**. |

Result tables: `evaluation/results/` (Goal 1) and `analysis/results/` (Goal 2). Goal 3: participant-level answers stay in the study sheet; the numbers above come from `evaluation/peer_trial_summary.py`.

Data-quality fixes that changed results: **duplicate ads** (the same job posted in several cities: 4,049 in the primary and 342 in the secondary target-role postings) are removed; a **role-pattern bug** put building/circuit design jobs under "ux designer" (31%) and is fixed; **Google** and **Facebook** were dropped as aliases after checking real postings (company names, not tools).

## How do I run the app?

Run every command below from the repo root (the folder with `main.py`). The only things you ever edit are the **CV path** and the **role**.

### 1. One-time setup

```bash
uv sync          # installs everything, including the skillradar package itself
uv run pytest    # should end with "... passed" (one expected xfail), nothing failed
```

### 2. Run the web app (the prototype)

```bash
uv run streamlit run app.py           # the prototype; opens in the browser
uv run streamlit run app_testing.py   # the same app + the user-study feedback form (step 5)
```

The three small files the apps read (`data/processed/posting_tools_*.csv`, `data/onet/software_skills.csv`) are committed, so the apps run straight after cloning. You only need the raw data ([Data requirements](#data-requirements)) to rebuild these tables or rerun the evaluation. To stop the app, press `ctrl+c` in the terminal.

Four steps (`skillradar/ui.py`, `.streamlit/config.toml`):

1. **Upload** a CV (`.pdf`, `.docx`, `.txt`, `.md`) or use the example CV.
2. **Pick a role and a dataset:** *All experience levels* (Jan 2024, US/UK/CA/AU, largest sample) or *Entry level & internships* (Apr 2024, US only).
3. **Check and correct the tools we found.** Each one shows the CV phrase it came from; untick wrong ones, add missed ones.
4. **Report.** An overview of how well the CV matches each of the five roles (Strong ≥ 50% / Partial ≥ 30% / Low coverage; it describes your tools, not your chances of being hired), then for the chosen role: the tools you already have, a radar chart (every top tool is a blip; closer to the centre = asked for more often; teal = on your CV, amber = missing), a coverage meter, and the missing tools with their 95% ranges, a plain-language key and a note on how many top places are stable. An entry-level vs. senior tag appears only when the difference is significant.

The CV is only held in memory. `app.py` saves nothing. "For the test facilitator" at the bottom shows how many tools the user removed/added.

### 3. User testing (peer trial)

`app_testing.py` is the version participants used. After the report, step 5 asks the six questionnaire statements (1–5), whether any missing tool is not really missing, "What was confusing?" and "What would you improve?", plus the facilitator's task codes. With the participant's consent it saves one anonymous row per session: participant code, role, dataset, sample or own CV, number of tools found/removed/added, ratings and comments. Never the CV or its file name.

- **Hosted** (Streamlit Community Cloud, main file `app_testing.py`): rows go to a shared Google Sheet configured in the app's Streamlit Secrets.
- **Locally:** rows go to `data/user_study/responses.csv` on that computer (gitignored).

```bash
# Goal 3 numbers: export the sheet as CSV into data/user_study/ (gitignored), then
uv run python evaluation/peer_trial_summary.py data/user_study/sheet_export.csv
```

The summary leaves out practice rows and the pilot (P01, P02). Setup, Google Sheet and deployment: [`user_testing/README_TESTING.md`](user_testing/README_TESTING.md). Protocol, consent text and tasks: [`evaluation/user_study.md`](evaluation/user_study.md). Pilot observations and what we changed: [`evaluation/pilot_notes.md`](evaluation/pilot_notes.md).

> [!IMPORTANT]
> The Google key lives only in Streamlit Secrets and in `.streamlit/secrets.toml` (gitignored). Never commit it. Participant-level results stay in the sheet; only summaries go into the report.

### 4. Command-line version

We use the command line for development and debugging. Put CVs in `data/cvs/` (gitignored, so CVs never end up on GitHub):

```bash
mkdir -p data/cvs
uv run python main.py report data/cvs/cv01.pdf "data scientist"
```

> [!IMPORTANT]
> **Privacy:** use neutral names (`cv01.pdf`, `cv02.pdf`, ...), not people's names. Only use a friend's CV with their OK, keep it on your own laptop, and delete it after the project.

Accepted formats: `.pdf`, `.docx`, `.txt`, `.md`. The PDF has to contain real text: a scanned image gives an error. Available roles: `data scientist`, `data analyst`, `software engineer`, `ml engineer`, `ux designer` (in quotes; case does not matter).

```bash
# entry-level and internship postings only (they exist in the secondary dataset only)
uv run python main.py report data/cvs/cv01.pdf "data scientist" --source secondary --level entry internship

# only UK postings, compared against the top 10 tools
uv run python main.py report data/cvs/cv01.pdf "software engineer" --country "United Kingdom" --top 10

# debugging: which words in the CV matched which tool
uv run python main.py report data/cvs/cv01.pdf "data scientist" --explain

# debugging: print the text the PDF reader extracted (includes contact details, don't paste it anywhere)
uv run python main.py report data/cvs/cv01.pdf "data scientist" --show-text
```

| Option | Default | What it does |
|---|---|---|
| `--source primary` / `secondary` | `primary` | `primary` = 1.3M postings, Jan 2024, US/UK/CA/AU. `secondary` = 124K postings, Apr 2024, US only, but with entry level + internships |
| `--level ...` | all levels | one or more of `entry`, `internship`, `associate`, `mid-senior`, `director`, `executive` |
| `--country "..."` | all countries | e.g. `"United States"`, `"United Kingdom"`, `"Canada"`, `"Australia"` (primary only) |
| `--top N` | `15` | compare against the N most-demanded tools for the role |
| `--min-share X` | `0.05` | ignore tools that appear in fewer than this share of postings (0.05 = 5%) |
| `--explain` | off | show which words in the CV matched which tool |
| `--show-text` | off | print the text extracted from the CV |

**How to read the report**

- **`in 54% of postings (51%-57%)`**: SQL is mentioned in 54% of the postings for this role. The range is a 95% Wilson confidence interval: the fewer postings, the wider it gets. Below 100 postings the report warns you.
- **`Your CV covers 42%`**: demand-weighted coverage of the top tools, so missing a tool that is in 80% of postings costs much more than missing one that is in 10%.
- **`Also on your CV, outside the top 15`**: tools you have that are less common for this role, with their share.
- The report judges **what the CV says**, not what you know. If you know SQL but never mention it, SQL shows up as missing.
- The O*NET flag column says "Hot Technology + In Demand" on almost every row, because our vocabulary only contains flagged tools. The web app does not show it.

### 5. Rebuild the job-market tables (needs the raw data)

```bash
uv run python main.py build --source primary      # streams the 5 GB job_summary.csv, around 3-10 minutes
uv run python main.py build --source secondary    # ~10 seconds
```

This runs the matcher over every posting for our five roles and saves `data/processed/posting_tools_<source>.csv`. Reports only read that file, which is why they are instant. When it is loaded, identical ad texts within a role are counted once (the same job is often posted in several cities).

> [!WARNING]
> **Rebuild after changing the matcher** (e.g. adding a word to `MANUAL_DROP` in `skillradar/matcher.py`). Otherwise the postings are matched with the old rules and your CV with the new ones.
>
> The evaluation uses the matcher as tagged `matcher-v1-frozen`. Changing the matcher after looking at test results would make the evaluation meaningless, so a changed matcher needs a new tag and newly labelled test items.

## Reproducing the evaluation

### Goal 1, keyword matcher

The posting texts are not ours to redistribute, so `evaluation/items/` is gitignored; `evaluation/sample_postings.py` recreates it from the raw data. The CV evaluation needs the CVs in `data/cvs/` (named as in the label file), which only we have.

```bash
uv run python evaluation/sample_postings.py              # done once (28 Oct); re-run only with --force, see evaluation/GUIDELINES.md
uv run python evaluation/evaluate.py --check evaluation/labels_A.csv                                 # how label names map onto O*NET
uv run python evaluation/evaluate.py --agreement evaluation/labels_A.csv evaluation/labels_B.csv     # labeller agreement
uv run python evaluation/merge_gold.py evaluation/labels_A.csv evaluation/labels_B.csv               # union -> labels_gold.csv (overwrites hand fixes!)
uv run python evaluation/evaluate.py evaluation/labels_gold.csv              # P/R for all ablation steps, test split
uv run python evaluation/evaluate.py evaluation/labels_gold_cv.csv --lenient # the 4 test CVs
uv run python scripts/alias_snippets.py                  # where suspicious aliases fire, for MANUAL_DROP decisions
```

### Goal 1, LLM methods

`skillradar/llm_matcher.py` adds three matchers next to the keyword matcher, all scored by the same `evaluate.py`:

| Matcher | What it does |
|---|---|
| `LLMOnly` | Gemini reads the text and lists every named tool with a quote (open vocabulary) |
| `Hybrid` | the frozen keyword matcher proposes candidates; Gemini keeps or rejects each in context and adds missed tools (after Clavié & Soulié 2023) |
| `HybridVerify` | ablation: only the keep/reject part of the same answer, no additions |

Every answer goes through a **grounding check** (a tool is kept only if its quote, or else its name, occurs in the text) and **linking** to O*NET through the same alias lookup as the labels; tools that do not link are kept under their own name. Few-shot examples come from dev items only. Nothing is trained. All API answers are cached in `data/llm_cache/` (gitignored). The LLM methods are used for the evaluation only, not in the app.

```bash
echo 'GEMINI_API_KEY=...' > .env                                             # key from aistudio.google.com; .env is gitignored
uv run python -m skillradar.llm_matcher --try "We use Python, Databricks and Power BI."   # connection check
uv run python evaluation/tune_llm.py                                          # dev split only
# frozen settings (tag llm-v1-frozen): copy the lines in evaluation/llm_frozen_settings.txt into your .env
uv run python evaluation/evaluate.py evaluation/labels_gold.csv --lenient --matcher full \
    skillradar.llm_matcher:LLMOnly skillradar.llm_matcher:Hybrid skillradar.llm_matcher:HybridVerify
```

The frozen run used `gemini-3.5-flash-lite` at temperature 0, few-shot examples `post_003` and `post_005`, and **no embedding linking** (threshold 1.0): on the dev split every embedding link was a related but different tool (BigQuery → MySQL, Kinesis → Kubernetes). Results: `evaluation/results/goal1_test_*.md`; the hand check of every lenient match is in `goal1_lenient_pairs.md`.

`--lenient` also credits out-of-vocabulary tools matched by name ("Amazon SageMaker" = "SageMaker"), for every matcher alike; strict scoring (the default) counts them as errors and is reported in the appendix of the paper. Never send CVs to the API without consent and a paid key.

### Goal 2

```bash
uv run python analysis/goal2.py > analysis/results/goal2_output.txt   # replication, rank stability, entry vs senior
```

Writes the tables (`ranks_*`, `replication_*`, `seniority_*`) and figures to `analysis/results/`.

## How does it work?

1. Tools are extracted from a free-text CV and normalised onto O*NET: the 301 tools flagged as **Hot Technology** or **In Demand**. Each tool gets aliases in four steps (exact name → without vendor → acronym → case rules for names that are also English words, like R, Go and Excel). In the web app the user then checks and corrects this list (human in the loop).
2. The same matcher runs on the full text of real job postings for the target role, so both sides use the same tool names. A posting's role comes from a pattern on its job title (`ROLE_PATTERNS` in `skillradar/demand.py`). Reposted ads (identical text) are counted once.
3. For each tool, **demand = share of postings for that role that mention it**, with a 95% Wilson interval.
4. Missing tools are ranked by demand, and the CV gets a demand-weighted coverage score over the top 15 tools.

> [!WARNING]
> **No "trending up or down".** Both job-posting datasets are **single snapshots** (a few days to two weeks of scraping each), so there is no time series. Comparing them (January vs. April 2024) mostly shows differences between the two scrapers: for software engineers 14 of the 15 significant changes go down. Goal 2 therefore tests whether the *current* ranking is robust and how it differs between entry-level and senior postings.

## Code

```bash
uv run pytest            # all tests; the ones needing data/onet/ are skipped if it's missing
uv run pytest -k matcher # only the matcher tests
```

Found a wrong match (e.g. "Go" in "Go further")? Add the sentence as a test in `tests/test_matcher.py` first, then fix `skillradar/matcher.py`, then rebuild.

| File | What it does |
|---|---|
| `main.py` | the command line: `build` and `report` |
| `app.py` | Streamlit web prototype: the 4-step flow (Upload → Role → Check → Report) |
| `app_testing.py` | participant version of `app.py` with the user-study form (step 5) |
| `skillradar/matcher.py` | O*NET keyword matcher, used for CVs and posting text. Hand-tuned lists (`CASE_SENSITIVE`, `MANUAL_DROP`, ...) are at the top |
| `skillradar/cv_parser.py` | CV file → clean text |
| `skillradar/demand.py` | `build`: postings → `data/processed/posting_tools_<source>.csv`; demand per tool for a role with 95% Wilson interval. Role title patterns are in `ROLE_PATTERNS` |
| `skillradar/report.py` | CV tools vs. role demand → ranked missing tools, demand-weighted coverage, match per role |
| `skillradar/variants.py` | ablation variants of the matcher (exact → vendor → acronym → full) |
| `skillradar/llm_matcher.py` | LLM-only, hybrid and verify-only matchers (Gemini), grounding check, linking, response cache |
| `skillradar/robustness.py` | Goal 2 statistics: replication (Spearman + bootstrap), rank intervals, entry vs senior (z-test + Benjamini-Hochberg) |
| `skillradar/study_logging.py` | saves anonymous study responses to the Google Sheet (hosted) or a local CSV; refuses any field that is not in the agreed list |
| `skillradar/ui.py` | the app's look: CSS and small HTML pieces (step bar, evidence rows, radar chart, bars with 95% ticks, coverage meter); all CV text is escaped |
| `evaluation/` | blind sampling, labelling guidelines, label files (A, B, gold, for postings and CVs), `evaluate.py`, `merge_gold.py`, `tune_llm.py`, `peer_trial_summary.py`, user-study protocol and pilot notes |
| `evaluation/results/` | Goal 1 result tables |
| `analysis/goal2.py`, `analysis/results/` | Goal 2 tables and figures |
| `scripts/alias_snippets.py` | shows where suspicious aliases fire, for MANUAL_DROP decisions |
| `user_testing/` | how to run and host the testing app and set up the Google Sheet |
| `preprocessing/` | data inspection notebooks (see below) |
| `tests/` | pytest suite |

## Data requirements

> [!IMPORTANT]
> This repo does **not** ship the raw data. `data/` is gitignored; you only need it to rebuild the tables or rerun the evaluation. None of the sources is ours to redistribute.
>
> The exception: the three small processed files the web app reads (`data/processed/posting_tools_primary.csv`, `posting_tools_secondary.csv`, `data/onet/software_skills.csv`) are committed, so the app works out of the box. They contain role, title, company and extracted tool names, not the posting texts.

Expected layout after downloading:

```
data/
├── cvs/                           # your own test CVs (cv01.pdf, ...), never committed
├── processed/                     # created by `main.py build`
├── kagglev2/                      # 1. primary job postings
│   ├── linkedin_job_postings.csv
│   ├── job_skills.csv
│   └── job_summary.csv
├── kaggle/                        # 2. secondary job postings
│   ├── postings.csv
│   └── ...                        (the rest of the unzipped folder; not used)
└── onet/                          # 3. skill taxonomy
    └── software_skills.csv
```

Kaggle setup (once):

```bash
pip install kaggle
# API token: kaggle.com/settings → "Create New Token" → downloads kaggle.json
mkdir -p ~/.kaggle && mv kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
```

### 1. Job postings (primary): 1.3M LinkedIn Jobs & Skills

[`asaniczka/1-3m-linkedin-jobs-and-skills-2024`](https://www.kaggle.com/datasets/asaniczka/1-3m-linkedin-jobs-and-skills-2024): ~1.35M LinkedIn postings, scraped 12–17 January 2024; 85% US, plus UK, Canada, Australia.

```bash
kaggle datasets download -d asaniczka/1-3m-linkedin-jobs-and-skills-2024 -p ./data/kagglev2 --unzip
```

Three files, linked by `job_link`: `linkedin_job_postings.csv` (title, company, location, `job_level`), `job_summary.csv` (full posting text, ~5 GB, streamed in chunks) and `job_skills.csv` (the dataset's own messy skill lists; used during inspection as a comparison, not as ground truth).

Why primary: 3–6× more postings per target role than the secondary dataset and full posting text. Limitations: only two experience levels (mid senior 89%, associate), so no entry-level or internship postings; the job mix follows the scraper's search list, not the real market.

License: [ODC-By 1.0](https://opendatacommons.org/licenses/by/1-0/) (DOI: 10.34740/kaggle/ds/4418374).

### 2. Job postings (secondary): LinkedIn Job Postings

[`arshkon/linkedin-job-postings`](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings): ~124K US LinkedIn postings, a single scrape from roughly 5–20 April 2024. Only `postings.csv` (full text in `description`, experience level) is used.

```bash
kaggle datasets download -d arshkon/linkedin-job-postings -p ./data/kaggle --unzip
```

We use it for two things the primary dataset can't do: **replication** of the demand ranking on an independent dataset (Goal 2), and **entry-level and internship** postings, which matter for students.

License: [ODbL](https://opendatacommons.org/licenses/odbl/).

### 3. Skill taxonomy: O*NET 31.0

[O*NET 31.0 Database](https://www.onetcenter.org/database.html) (August 2026 release), licensed [CC BY 4.0](https://www.onetcenter.org/license_db.html). Under "Tabular data files" pick **CSV** → **All files (ZIP)**; no account needed. Only `software_skills.csv` is used: it maps specific tools (Docker, AWS, Python, ...) to occupations and carries the Hot Technology / In Demand flags our vocabulary is built from.

> [!NOTE]
> O*NET names tools in a way nobody writes in a job ad (*"Structured query language SQL"*, *"Amazon Web Services AWS software"*), so the matcher generates shorter aliases (SQL, AWS, Power BI without "Microsoft") and matches ambiguous names like R, Go and Excel case-sensitively.

## Notebooks

| Notebook | What it does |
|---|---|
| [`preprocessing/data_inspection_primary.ipynb`](preprocessing/data_inspection_primary.ipynb) | Inspects the 1.3M dataset: time coverage, roles, skill labels, our matcher vs. the dataset's own skills, January vs. April snapshot comparison |
| [`preprocessing/data_inspection_secondary.ipynb`](preprocessing/data_inspection_secondary.ipynb) | Inspects the 124K dataset and O*NET: time coverage, Kaggle's skill categories, first keyword-matcher baseline |

Both end with a **Findings → decisions** table. They are exploration from weeks 1–5: they load the raw data directly and do not remove duplicate ads, so the numbers to report come from `analysis/goal2.py` and `evaluation/evaluate.py`.

## Project docs

Decisions log and week-by-week status: [`TODO.md`](TODO.md). Findings and material for the paper: [`report_draft.md`](report_draft.md). Earlier notes on motivation, risks, literature and the lightning/pre-mortem presentations: [`notes/`](notes/). Labelling rules: [`evaluation/GUIDELINES.md`](evaluation/GUIDELINES.md). User-study protocol: [`evaluation/user_study.md`](evaluation/user_study.md).

> [!IMPORTANT]
> Do not commit anything else from `data/` (CVs, raw datasets, study responses).