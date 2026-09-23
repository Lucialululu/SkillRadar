# SkillRadar
SkillRadar: A CV-to-job-market skill-gap tool for job-seeking students, 02830 Advanced Project in Digital Media Engineering

<p align="center">
  <img src="skillradar_logo.png" width="350" alt="SkillRadar Logo">
</p>

## What is this?

Every student job-hunting for an internship or first grad role runs into the same wall: it's hard to know, in concrete terms, which skills employers are actually asking for right now, whether your CV reflects that, and which gaps are actually worth closing before a deadline. LinkedIn's "skill match" needs a paid account and only compares you to one posting at a time. Generic CV checkers give vague advice.

SkillRadar takes your CV and a target role, compares your skills against real, aggregated job-posting data for that role, and tells you what's missing, how common it is, and whether demand for it is rising or falling.

```
CV → extract & normalize skills → compare against job-postings data → rank missing skills by demand + trend
```

**Example output:**
```
Docker   - missing - in 42% of postings - ↑ rising demand
Azure    - missing - in 31% of postings - ↑ rising demand
```

> [!NOTE]
> This is a group project for DTU course 02830 (Advanced Project in Digital Media Engineering), not a polished consumer product. Scope, data, and Z everything below is very much a moving target as we build.

## How do I run the app?

*(will be filled in once `main.py` exists but same pattern as: `uv sync` → `source .venv/bin/activate` → `python main.py`)*

## How does it work?

1. Skills are extracted from a free-text CV and normalized against a structured skill taxonomy (O*NET).
2. The same normalization is applied to a large set of job postings for the target role, so both sides are comparable.
3. For each skill in demand for that role, we compute how common it is (% of postings) and whether that demand is trending up or down within the data window.
4. Missing + trending-up skills get surfaced first.

> [!IMPORTANT]
> We're also testing whether the taxonomy-normalization step is actually worth its complexity, vs. simple keyword matching. See `course_notes lighting_presentation_W3.md` for why this is a real design question and not just an implementation detail.

## Data requirements

> [!IMPORTANT]
> This repo does **not** ship any data. `data/` is gitignored, so you need to create it yourself and download the two sources below into it. Neither dataset is small, and neither is ours to redistribute, so this step is on you.

```bash
mkdir data
```

### 1. Job postings - Kaggle

We use [`arshkon/linkedin-job-postings`](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) (around 124K LinkedIn postings, 2023–2024).

```bash
pip install kaggle
# grab an API token first: kaggle.com/settings → "Create New Token" → downloads kaggle.json
mkdir -p ~/.kaggle && mv kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json

kaggle datasets download -d arshkon/linkedin-job-postings -p ./data --unzip
```

> [!TIP]
> We just keep the whole unzipped Kaggle folder in `data/` for now and filter down to the files we actually use in code, rather than manually deleting things. The files that matter are:
> - `postings.csv` - main table, has `listed_time` / `original_listed_time` for the trend bucketing
> - `jobs/job_skills.csv` - skill codes per posting
> - `mappings/skills.csv` - skill code → human-readable name lookup
>
> `jobs/benefits.csv`, `jobs/salaries.csv`, and everything under `companies/` are not used - see [DELIMITATION](course_notes/project_draft.md) (no salary prediction, no company-level analysis).

> [!NOTE]
> The dataset only spans ~1–1.5 years (2023–2024), not the "multiple years" originally scoped in the project draft. We've adjusted "trend" to mean **quarter-over-quarter within that window**, not year-over-year. At ~7-10K postings/month this still gives enough volume per skill for a > meaningful signal.

License: [ODbL](https://opendatacommons.org/licenses/odbl/) - fine for coursework/research, cited accordingly in our report.

### 2. Skill taxonomy - O*NET

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

**Download:** go to the link above → under "Tabular data files" pick **CSV** → click **"All files (ZIP)"**. No account needed (that's only for the live lookup API, not the flat files).

> [!WARNING]
> The O*NET zip has **45 files**. Almost all of it is out of scope for us (abilities, work styles, work context, career interests, education/training requirements, job zones, tasks, survey scale metadata — none of it touches "what skills does this role need"). Unlike the Kaggle folder, we actually deleted the unused ones rather than filtering in code, because 45 files of mostly-irrelevant worker-characteristics data was too much noise to leave lying around.
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

## Project docs

More detail on motivation, goals, testing plan, risks, and the week-by-week plan lives in [`course_notes/`](course_notes/).

> [!IMPORTANT]
> Do not commit anything from `data/` to Git. Both datasets are large and neither is ours to redistribute — that's exactly why it's gitignored.
