# SkillRadar
SkillRadar: A CV-to-job-market skill-gap tool for job-seeking students, 02830 Advanced Project in Digital Media Engineering

<p align="center">
  <img src="skillradar_logo.png" width="350" alt="SkillRadar Logo">
</p>

## What is this?

Every student job-hunting for an internship or first grad role runs into the same wall: it's hard to know, in concrete terms, which skills employers are actually asking for right now, whether your CV reflects that, and which gaps are actually worth closing before a deadline. LinkedIn's "skill match" needs a paid account and only compares you to one posting at a time. Generic CV checkers give vague advice.

SkillRadar takes your CV and a target role, compares your skills against real, aggregated job-posting data for that role, and tells you what's missing, how common it is, and whether employers are flagging it as in demand.

```
CV → extract & normalize skills → compare against job-postings data → rank missing skills by demand
```

**Example output** (data scientist, numbers from our actual data):
```
AWS       - missing - in 24% of data scientist postings - O*NET "hot technology"
Tableau   - missing - in 21% of data scientist postings - O*NET "hot technology"
PyTorch   - missing - in 13% of data scientist postings - O*NET "hot technology"
```

> [!NOTE]
> This is a group project for DTU course 02830 (Advanced Project in Digital Media Engineering), not a polished consumer product. Scope, data, and everything below is very much a moving target as we build.

## How do I run the app?

*(will be filled in once `main.py` exists, same pattern as: `uv sync` → `source .venv/bin/activate` → `python main.py`)*

For now, the work lives in notebooks:

```bash
uv sync
source .venv/bin/activate
jupyter notebook preprocessing/
```

## How does it work?

1. Skills are extracted from a free-text CV and normalized against a structured skill taxonomy (O*NET). We use the ~300 tools O*NET flags as **Hot Technology** or **In Demand**, i.e. the tools employers actually ask for.
2. The same matcher runs on the full text of real job postings for the target role, so both sides use the same skill names.
3. For each skill we compute **demand = % of postings for that role that mention it** (counted once per posting).
4. Missing skills are ranked by demand, with O*NET's Hot Technology / In Demand flag shown next to them.

> [!IMPORTANT]
> We're also testing whether the taxonomy-normalization step is actually worth its complexity, vs. simple keyword matching. See [`draft_notes/lighting_presentation_W3.md`](draft_notes/lighting_presentation_W3.md) for why this is a real design question and not just an implementation detail.

> [!WARNING]
> **"Trending up or down" is on hold.** The original plan was to measure how demand changes over time, but both job-posting datasets turned out to be **single snapshots** (a few days to two weeks of scraping each), so there is no time series to measure a trend on. Comparing the two snapshots (January vs. April 2024) mostly shows differences between the two scrapers, not the market. We are redefining this part: currently O*NET's Hot Technology / In Demand flags as the demand signal, plus a stability test (do the skill rankings for a role hold across both snapshots?). See `preprocessing/data_inspection_primary.ipynb`, section 5.

## Data requirements

> [!IMPORTANT]
> This repo does **not** ship any data. `data/` is gitignored, so you need to create it yourself and download the three sources below into it. None of them is small, and none is ours to redistribute, so this step is on you.

Expected layout after downloading:

```
data/
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
- **Replication:** checking that skill demand holds on an independent dataset. It does: for data scientists, Python / SQL / R / AWS / PyTorch land within ~2 percentage points across both datasets.
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

## Project docs

More detail on motivation, goals, testing plan, risks, and the week-by-week plan lives in [`draft_notes/`](draft_notes/).

> [!IMPORTANT]
> Do not commit anything from `data/` to Git. All datasets are large and none is ours to redistribute — that's exactly why it's gitignored.
