# SkillRadar
SkillRadar: A CV-to-job-market skill-gap tool for job-seeking students, 02830 Advanced Project in Digital Media Engineering

<!-- <p align="center">
  <img src="skillradar_logo.png" width="350" alt="SkillRadar Logo">
</p> -->

## Our goals

**Aim:** we aim to create a web prototype where a job-seeking student uploads their CV, picks a target role, and gets a ranked list of the tools they are missing, with evidence from real job postings.

### Goal 1: Extract tools reliably from CVs and job postings
Map free text (CVs and postings) onto one shared vocabulary of tools and technologies (O*NET Hot Technology / In Demand), so both sides can be compared tool by tool. In this project, a *skill* means a named tool you can use.

**How we test it**

> Hand-label tools in 40 data-scientist postings (10 dev / 30 test, drawn once with seed 42, see `evaluation/manifest.csv`) and 6–10 CVs *before* running the matcher. Report results only on the held-out test items, with the matcher frozen beforehand (`git tag matcher-v1-frozen`).

> Precision and recall per side (postings, CVs).

> Two of us label the same 15 postings independently → agreement (F1 between labellers, Cohen's kappa), to show the labels themselves are reliable.

> Ablation: how much each normalisation step adds (exact O*NET names → + vendor stripping → + acronyms → + case rules).

> Method comparison: keyword matcher vs. a pretrained LLM vs. a hybrid (keyword proposes candidates, the LLM verifies them in context), on the same held-out labels.

> Target (set before measuring): precision ≥ 0.85 and recall ≥ 0.75 on held-out postings.

### Goal 2: Measure current tool demand per role, and show it is robust
For each role, the share of postings that mention each tool, with 95% confidence intervals. Show that this ranking replicates across two independent datasets, and how demand differs between entry-level and senior postings.

**How we test it**

> Rank correlation (Spearman) of the top-20 tools per role between the two datasets (Jan 2024 vs Apr 2024). Target: ρ ≥ 0.8 for data scientist, data analyst and software engineer.

> Bootstrap intervals on each tool's rank, to show which positions in the ranking are actually stable.

> Entry-level vs. mid-senior postings within the same dataset: two-proportion tests per tool, corrected for multiple comparisons.

### Goal 3: A prototype students can use and find useful
A web interface: upload CV → choose role → check and correct the tools we found → skill-gap report (missing tools ranked by demand, 95% ranges, coverage score, entry-level vs. senior view).

**How we test it**

> Pilot with 2 classmates, then a peer trial with 6–8 job-seeking students using their own CV, with think-aloud on fixed tasks.

> Task success: can they get and read a report without help?

> Perceived accuracy: for each "missing" tool, do they agree it is really missing from their CV?

> Usefulness and trust: short questionnaire (Likert) on whether the report would change what they learn or apply for next, and whether they would act on it.

> Correction rate: how many found tools users remove (false positives) or add (misses) in the confirm step. A second, real-world measurement for Goal 1.

### Stretch goals (only if Goals 1–3 are done)

> Single job-ad mode: compare the CV with one specific ad, and show how common each requested tool is across the role.

> A short learning suggestion per missing tool.

### Not our goals (delimitation)

> **No trends over time.** Both datasets are single snapshots (Jan and Apr 2024). Our January versus April comparison showed differences between the scrapers, not the market, so we make no rising/falling claims.

> **Tools only, not skills in general.** "Machine learning", "statistics" or soft skills are not in our vocabulary. Coverage means coverage of tool demand.

> **The report judges what the CV says,** not what the person knows.

> **Data is LinkedIn 2024, around 85% US.** We do not claim it represents the Danish job market.

> No salary prediction, no application automation, no hiring guarantee.

## Results so far (week 8)

| Goal | Status | Result |
|---|---|---|
| 1 · Extraction | test set drawn, labelling in progress | Indirect check only so far: our text matcher agrees with the primary dataset's own skill labels within ~3 points for 23 of the top 25 data-scientist tools |
| 2 · Robust demand | ✅ analysed | Rankings replicate across the two datasets: Spearman ρ = 0.87 (data analyst), 0.87 (software engineer), 0.80 (data scientist), 0.82 (ML engineer, small sample), 0.63 (UX designer). Top 3–7 tools per role have stable ranks. Few entry vs. senior differences survive correction; clearest: data-analyst entry ads ask for SQL far less often (36% vs 66%) |
| 3 · Prototype | ✅ v1 built, user tests pending | `app.py` |

Data-quality fixes that changed results: **duplicate ads** (the same job posted in several cities: 4,049 in the primary and 342 in the secondary target-role postings) are now removed; a **role-pattern bug** put building/circuit design jobs under "ux designer" (31%); **Google** and **Facebook** were dropped as aliases after checking real postings (company names, not tools). Full tables: `analysis/results/`, numbers and decisions: [`TODO.md`](TODO.md).

## What is this?

Every student job-hunting for an internship or first grad role runs into the same wall: it's hard to know, in concrete terms, which skills employers are actually asking for right now, whether your CV reflects that, and which gaps are actually worth closing before a deadline. LinkedIn's "skill match" needs a paid account and only compares you to one posting at a time. Generic CV checkers give vague advice.

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
> This is a 2-person group project for DTU course 02830 (Advanced Project in Digital Media Engineering), a research prototype, not a consumer product. Current status and plan: [`TODO.md`](TODO.md).

## How do I run the app?

Run every command below from the repo root (the folder with `main.py`). All commands can be copy-pasted as they are; the only things you ever edit are the **CV path** and the **role**, marked below.

### 1. One-time setup

```bash
uv sync          # installs everything, including the skillradar package itself
uv run pytest    # should end with "... passed", nothing failed
```

You also need the data in `data/`, see [Data requirements](#data-requirements) below.

### 2. Build the job-market tables (once)

```bash
uv run python main.py build --source primary      # streams the 5 GB job_summary.csv, takes around 3-10 minutes
uv run python main.py build --source secondary    # ~10 seconds; needed for entry-level data and Goal 2
```

This runs the skill matcher over every posting for our five roles once and saves the result to `data/processed/posting_tools_<source>.csv` (a few MB, gitignored). Every report afterwards only reads that small file, which is why reports are instant. When the file is loaded, identical ad texts within a role are counted once (the same job is often posted in several cities).

> [!WARNING]
> **Rebuild after changing the matcher** (e.g. adding a word to `MANUAL_DROP` in `skillradar/matcher.py`). Otherwise the postings are still matched with the old rules while your CV is matched with the new ones.
>
> The Goal 1 evaluation uses the matcher as tagged `matcher-v1-frozen`. Changing the matcher after looking at test results would make the evaluation meaningless, so changes go into a new tag and the evaluation is rerun.

### 3. Run the web app (the prototype)

```bash
uv run streamlit run app.py      # opens in the browser; needs step 2 (both sources for all features)
```

Upload a CV (or tick the example CV) → pick a role and dataset → **check and correct the tools we found** (each one shows the CV phrase it came from) → report with 95% ranges, coverage and an entry-level vs. senior column. The CV is only held in memory. "For the test facilitator" at the bottom shows how many tools the user removed/added, for the peer-trial notes; nothing is saved.

The steps below are the **command-line version**, which we use for development and debugging.

### 4. Add your CV

Put CVs in `data/cvs/`. Like everything in `data/`, that folder is gitignored, so CVs never end up on GitHub.

```bash
mkdir -p data/cvs
```

Accepted formats: `.pdf`, `.docx`, `.txt`, `.md`. The PDF has to contain real text: a scanned image will give an error.

> [!IMPORTANT]
> **Privacy:** use neutral names (`cv01.pdf`, `cv02.pdf`, ...), not people's names. Only use a friend's CV with their OK, keep it on your own laptop, and delete it after the project. The app only reads CVs into memory and never saves their text anywhere.

### 5. Get your skill-gap report

```bash
uv run python main.py report data/cvs/cv01.pdf "data scientist"
```

Available roles: `data scientist`, `data analyst`, `software engineer`, `ml engineer`, `ux designer` (written in quotes; case does not matter).

More examples:

```bash
# entry-level and internship postings only (they exist in the secondary dataset only)
uv run python main.py report data/cvs/cv01.pdf "data scientist" --source secondary --level entry internship

# only UK postings, compared against the top 10 tools
uv run python main.py report data/cvs/cv01.pdf "software engineer" --country "United Kingdom" --top 10

# debugging: which words in the CV matched which tool
uv run python main.py report data/cvs/cv01.pdf "data scientist" --explain

# debugging: print the text the PDF reader extracted (includes your contact details, don't paste it anywhere)
uv run python main.py report data/cvs/cv01.pdf "data scientist" --show-text
```

All options (also shown by `uv run python main.py report --help`):

| Option | Default | What it does |
|---|---|---|
| `--source primary` / `secondary` | `primary` | `primary` = 1.3M postings, Jan 2024, US/UK/CA/AU. `secondary` = 124K postings, Apr 2024, US only, but with entry level + internships |
| `--level ...` | all levels | one or more of `entry`, `internship`, `associate`, `mid-senior`, `director`, `executive` |
| `--country "..."` | all countries | e.g. `"United States"`, `"United Kingdom"`, `"Canada"`, `"Australia"` (primary only) |
| `--top N` | `15` | compare against the N most-demanded tools for the role |
| `--min-share X` | `0.05` | ignore tools that appear in fewer than this share of postings (0.05 = 5%) |
| `--explain` | off | show which words in the CV matched which tool |
| `--show-text` | off | print the text extracted from the CV |

### 6. How to read the report

- **`in 55% of postings (52%-58%)`**: SQL is mentioned in 55% of the postings for this role. The range in brackets is a 95% confidence interval: the fewer postings, the wider it gets. Below 100 postings the report warns you.
- **`Your CV covers 42%`**: demand-weighted coverage of the top tools, so missing a tool that is in 80% of postings costs much more than missing one that is in 10%.
- **`Also on your CV, outside the top 15`**: tools you have that are less common for this role, with their share.
- The report judges **what the CV says**, not what you know. If you know SQL but never mention it, SQL shows up as missing, which is useful to know too.
- The O*NET flag column says "Hot Technology + In Demand" on almost every row, because our vocabulary only contains flagged tools. It will be removed.

### Evaluation (Goal 1) and analysis (Goal 2)

```bash
uv run python scripts/alias_snippets.py                  # evidence for MANUAL_DROP decisions (Google, Facebook, C, Go)
uv run python evaluation/sample_postings.py              # done once (28 Oct); re-run only with --force, see evaluation/GUIDELINES.md
uv run python evaluation/evaluate.py --check evaluation/labels_<you>.csv
uv run python evaluation/evaluate.py --agreement evaluation/labels_A.csv evaluation/labels_B.csv
uv run python evaluation/evaluate.py evaluation/labels_gold.csv          # P/R for all ablation steps, test split
uv run python analysis/goal2.py > analysis/results/goal2_output.txt   # replication, rank stability, entry vs senior
```

### Tests and code

```bash
uv run pytest            # all tests; the ones needing data/onet/ are skipped if it's missing
uv run pytest -k matcher # only the matcher tests
```

Found a wrong match (e.g. "Go" in "Go further")? Add the sentence as a test in `tests/test_matcher.py` first, then fix `skillradar/matcher.py`, then rebuild (step 2).

| File | What it does |
|---|---|
| `main.py` | the command line: `build` and `report` |
| `skillradar/matcher.py` | O*NET keyword matcher, used for CVs, posting text and dataset labels. Hand-tuned lists (`CASE_SENSITIVE`, `MANUAL_DROP`, ...) are at the top |
| `skillradar/cv_parser.py` | CV file → clean text |
| `skillradar/demand.py` | `build`: postings → `data/processed/posting_tools_<source>.csv`; query: % of postings per tool for a role (with 95% Wilson interval). Role title patterns are in `ROLE_PATTERNS` |
| `skillradar/report.py` | CV tools vs. role demand → ranked missing skills + demand-weighted coverage |
| `skillradar/variants.py` | ablation variants of the matcher (exact → vendor → acronym → full) |
| `skillradar/robustness.py` | Goal 2 statistics: replication (Spearman + bootstrap), rank intervals, entry vs senior (z-test + Benjamini-Hochberg) |
| `app.py` | Streamlit web prototype |
| `evaluation/` | blind sampling, labelling guidelines, `evaluate.py` (precision/recall, agreement) |
| `analysis/goal2.py` | Goal 2 tables and figures |
| `scripts/alias_snippets.py` | shows where suspicious aliases fire, for MANUAL_DROP decisions |

## How does it work?

1. Tools are extracted from a free-text CV and normalised onto a structured taxonomy (O*NET). We use the ~300 tools O*NET flags as **Hot Technology** or **In Demand**, i.e. the tools employers actually ask for. In the web app the user then checks and corrects this list (human in the loop).
2. The same matcher runs on the full text of real job postings for the target role, so both sides use the same tool names. Reposted ads (identical text) are counted once.
3. For each tool we compute **demand = % of postings for that role that mention it** (counted once per posting), with a 95% Wilson interval.
4. Missing tools are ranked by demand, and the CV gets a demand-weighted coverage score. Goal 2 checks that the ranking replicates across two independent datasets.

> [!IMPORTANT]
> We test whether each normalisation step is worth it (ablation), and whether a pretrained LLM that reads the context does better than keyword matching (method comparison). O*NET stays the vocabulary in both cases: the taxonomy is *what* we map to, the matcher or model is *how*.

> [!WARNING]
> **No "trending up or down".** Both job-posting datasets are **single snapshots** (a few days to two weeks of scraping each), so there is no time series. Comparing them (January vs. April 2024) mostly shows differences between the two scrapers: for software engineers 14 of the 15 significant changes go down. Instead, Goal 2 tests whether the *current* ranking is robust (it replicates across both datasets) and how it differs between entry-level and senior postings. See `preprocessing/data_inspection_primary.ipynb` section 5 and `analysis/goal2.py`.

## Data requirements

> [!IMPORTANT]
> This repo does **not** ship any data. `data/` is gitignored, so you need to create it yourself and download the three sources below into it. None of them is small, and none is ours to redistribute, so this step is on you.

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
│   ├── jobs/        (job_skills.csv, job_industries.csv, ...)
│   ├── mappings/    (skills.csv, industries.csv)
│   └── companies/   (not used)
└── onet/                          # 3. skill taxonomy
    ├── software_skills.csv
    ├── occupation_data.csv
    ├── job_titles.csv
    ├── essential_skills.csv
    ├── transferable_skills.csv
    └── related_occupations.csv
```

Kaggle setup (once):

```bash
pip install kaggle
# grab an API token first: kaggle.com/settings → "Create New Token" → downloads kaggle.json
mkdir -p ~/.kaggle && mv kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
```

### 1. Job postings (primary) - Kaggle, 1.3M LinkedIn Jobs & Skills

We use [`asaniczka/1-3m-linkedin-jobs-and-skills-2024`](https://www.kaggle.com/datasets/asaniczka/1-3m-linkedin-jobs-and-skills-2024) (~1.35M LinkedIn postings, scraped January 12–17, 2024; US 85%, plus UK, Canada, Australia).

```bash
kaggle datasets download -d asaniczka/1-3m-linkedin-jobs-and-skills-2024 -p ./data/kagglev2 --unzip
```

> [!TIP]
> Three files, all linked by `job_link` (the LinkedIn url):
> - `linkedin_job_postings.csv` - one row per posting: title, company, location, `first_seen`, `job_level`
> - `job_skills.csv` - a comma-separated skill list per posting (~21 skills each, 96% coverage). Tool-level (Python, SQL, Docker) but messy: 2.77M distinct spellings. We use it as a benchmark and synonym source, **not** as ground truth.
> - `job_summary.csv` - the full posting text. **~5 GB**, so our notebooks stream it in chunks and never load it whole.

Why this one is primary: 3–6× more postings per target role than the secondary dataset, full posting text, and skill labels that agree with our own matcher to within ~3 percentage points for most tools.

Known limitations: only two experience levels (`Mid senior` 89%, `Associate`), so **no entry-level or internship postings**. `job_type` is 99% "Onsite" (looks like a scraper default, not usable). The job mix follows the scraper's search list, not the real market.

License: [ODC-By 1.0](https://opendatacommons.org/licenses/by/1-0/) - fine for coursework/research, cited accordingly in our report (DOI: 10.34740/kaggle/ds/4418374).
<!-- TODO: double-check the license shown on the Kaggle page before hand-in -->

### 2. Job postings (secondary) - Kaggle, LinkedIn Job Postings

We also use [`arshkon/linkedin-job-postings`](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) (~124K US LinkedIn postings, a single scrape from roughly April 5–20, 2024).

```bash
kaggle datasets download -d arshkon/linkedin-job-postings -p ./data/kaggle --unzip
```

We keep it for two things the primary dataset can't do:
- **Replication:** checking that tool demand holds on an independent dataset. It does for most roles: Spearman ρ of the tool ranking is 0.80–0.87 for data scientist, data analyst and software engineer (`analysis/goal2.py`).
- **Entry level:** it includes `Entry level` (~37K) and `Internship` (~1.4K) postings, which matter for our actual users (students).

> [!TIP]
> We keep the whole unzipped folder in `data/kaggle/` and filter in code. The files that matter are:
> - `postings.csv` - main table, full posting text in `description`
> - `jobs/job_skills.csv` + `mappings/skills.csv` - only 35 broad job categories (Sales, IT, ...), not tool-level skills, so at most a coarse role filter
>
> `jobs/benefits.csv`, `jobs/salaries.csv`, and everything under `companies/` are not used - see [DELIMITATION](draft_notes/project_draft.md) (no salary prediction, no company-level analysis).

License: [ODbL](https://opendatacommons.org/licenses/odbl/) - fine for coursework/research, cited accordingly in our report.
<!-- TODO: another source lists this dataset as CC BY-SA 4.0, check the Kaggle page -->

### 3. Skill taxonomy - O*NET

O*NET 31.0 Database
August 2026 Release
-------------------

For information on current and future releases of the O*NET database,
please visit:

https://www.onetcenter.org/database.html

For documentation on the contents and structure of these files,
please visit:

https://www.onetcenter.org/dictionary/31.0/csv/

The content of the O*NET 31.0 Database is licensed under a Creative Commons Attribution 4.0 International License. For more information, please visit:

https://www.onetcenter.org/license_db.html

**Download:** go to the link above → under "Tabular data files" pick **CSV** → click **"All files (ZIP)"**. No account needed (that's only for the live lookup API, not the flat files). Put the kept files in `data/onet/`.

> [!WARNING]
> The O*NET zip has **45 files**. Almost all of it is out of scope for us (abilities, work styles, work context, career interests, education/training requirements, job zones, tasks, survey scale metadata — none of it touches "what skills does this role need"). Unlike the Kaggle folders, we actually deleted the unused ones rather than filtering in code, because 45 files of mostly-irrelevant worker-characteristics data was too much noise to leave lying around.
>
> **Kept:**
> - `software_skills.csv` — the actual taxonomy: specific tools/tech (Docker, AWS, Python, ...) mapped to occupations, including "Hot Technology" / "In Demand" flags. This is the core matching taxonomy.
> - `occupation_data.csv` — SOC code + occupation title + description.
> - `job_titles.csv` — alternate/lay job titles per occupation, used to map a user's free-text role input (e.g. "data scientist") to an occupation code.
>
> **Kept in reserve, not used yet:**
> - `essential_skills.csv`, `transferable_skills.csv` — O*NET's general skill *categories* (e.g. "Programming," "Critical Thinking"), as opposed to `software_skills.csv`'s specific tools. Might layer these in later for a "broader skill area" view.
> - `related_occupations.csv` — only relevant for the stretch goal (suggesting adjacent roles).
>
> Everything else got yeeted.

> [!NOTE]
> O*NET names tools in a way nobody writes in a job ad (*"Structured query language SQL"*, *"Amazon Web Services AWS software"*), so our matcher generates shorter aliases (SQL, AWS, Power BI without "Microsoft") and matches ambiguous names like R, Go and Excel case-sensitively. The details and why are in the inspection notebooks.

## Notebooks

| Notebook | What it does |
|---|---|
| [`preprocessing/data_inspection_primary.ipynb`](preprocessing/data_inspection_primary.ipynb) | Inspects the 1.3M dataset: time coverage, roles, skill labels, our O*NET matcher vs. the dataset's own skills, January vs. April snapshot comparison |
| [`preprocessing/data_inspection_secondary.ipynb`](preprocessing/data_inspection_secondary.ipynb) | Inspects the 124K dataset and O*NET: time coverage, Kaggle's skill categories, role → occupation lookup, first keyword-matcher baseline |

Both end with a **Findings → decisions** table.

> [!NOTE]
> The notebooks are exploration from weeks 1–5. They use the shared matcher (`skillradar/matcher.py`) but load the raw data directly, so they do not remove duplicate ads. The numbers to report come from `analysis/goal2.py` and `evaluation/evaluate.py`.

## Project docs

Status, plan, decisions and open questions: [`TODO.md`](TODO.md). Earlier notes on motivation, risks and the lightning/premortem presentations: [`draft_notes/`](draft_notes/). Labelling rules: [`evaluation/GUIDELINES.md`](evaluation/GUIDELINES.md).

> [!IMPORTANT]
> Do not commit anything from `data/` to Git. All datasets are large and none is ours to redistribute — that's exactly why it's gitignored.