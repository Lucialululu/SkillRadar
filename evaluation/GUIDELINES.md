# Labelling guidelines (Goal 1 evaluation)

The labels are our ground truth, so they must come from a **human reading the text**,
before anyone looks at what the matcher found. Never paste matcher or LLM output into
a label file.

## Setup

1. `uv run python evaluation/sample_postings.py` (once; commit `manifest.csv`)
2. Copy `labels_TEMPLATE.csv` to `labels_<yourname>.csv` and fill in `labeller` with your name.
3. Open `evaluation/items/post_XXX.txt` and write the tools in `true_tools`.
4. CVs: add rows yourself, `item_id` = the CV file name without extension (`cv01`, ...),
   `split` = `dev` for the CVs we already used while building (cv01), `test` for new ones.
   The CV stays in `data/cvs/`, only its tools go in the label file.

## What counts as a tool

Write down every **named tool or technology** that the text says the person uses / the job requires
or mentions as part of the work: programming languages, libraries, databases, cloud platforms,
BI tools, office software, ML frameworks, version control, etc.

- **Yes:** "Python", "experience with AWS", "dashboards in Tableau", "Git", "R", "Excel".
- **No:** company names that are not used as a tool ("Google is an equal opportunity employer",
  "Join Facebook's team"), English words ("Go further", "excel at communication", "C-level"),
  general skills ("machine learning", "statistics", "communication").
- **Write every tool, also ones you think our vocabulary does not have** (e.g. "Jupyter", "uv").
  `evaluate.py` reports recall both on all tools and on the ones in our O*NET vocabulary, and the
  out-of-vocabulary share is a result in itself.
- Each tool once per item, even if mentioned five times.

## Format

`true_tools` = tool names separated by `;`, written the way people write them:

    Python; SQL; AWS; Power BI; scikit-learn; Jupyter

`evaluate.py` maps these onto O*NET names (SQL -> "Structured query language SQL").
Run `uv run python evaluation/evaluate.py --check labels_<you>.csv` to see which names it could
not map: fix typos, leave real out-of-vocabulary tools as they are.

`notes`: anything unsure ("'Spark' could be the company name here").

## Agreement (two labellers)

Both of us label the same **15 test postings** independently (don't discuss them first), then:

    uv run python evaluation/evaluate.py --agreement labels_A.csv labels_B.csv

Afterwards we discuss the disagreements and write one agreed file `labels_gold.csv`, which is what
the evaluation uses. The agreement numbers go in the report.
