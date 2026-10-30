# Labelling guidelines (Goal 1 evaluation)

The labels are our ground truth, so they must come from a **human reading the text**,
before anyone looks at what the matcher found. Never paste matcher or LLM output into
a label file.

## Setup

1. ~~`uv run python evaluation/sample_postings.py`~~ Done on 28 Oct (40 postings, 10 dev / 30 test,
   seed 42; `manifest.csv` is committed). Do not run it again: the sample is fixed.
2. Copy the template and fill in `labeller` with your name:

       cp evaluation/labels_TEMPLATE.csv evaluation/labels_<yourname>.csv

3. Open `evaluation/items/post_XXX.txt` and write the tools in `true_tools`.
   Rows without a labeller are ignored, so a half-finished file can already be checked and evaluated.
4. CVs: add rows yourself, `item_id` = the CV file name without extension (`cv01`, ...),
   `split` = `dev` for the CVs we already used while building (cv01), `test` for new ones.
   The CV stays in `data/cvs/`, only its tools go in the label file.

## What counts as a tool

We will write down every **named tool or technology** that the text says the person uses / the job requires
or mentions as part of the work: programming languages, libraries, databases, cloud platforms,
BI tools, office software, ML frameworks, version control, etc.

- **Yes:** "Python", "experience with AWS", "dashboards in Tableau", "Git", "R", "Excel".
- **No:** company names that are not used as a tool ("Google is an equal opportunity employer",
  "Join Facebook's team"), English words ("Go further", "excel at communication", "C-level"),
  general skills ("machine learning", "statistics", "communication").
- **Write every tool, also ones we think our vocabulary does not have** (e.g. "Jupyter", "uv").
  `evaluate.py` reports recall both on all tools and on the ones in our O*NET vocabulary, and the
  out-of-vocabulary share is a result in itself.
- Each tool once per item, even if mentioned five times.

## Format

`true_tools` = tool names separated by `;`, written the way people write them:

    Python; SQL; AWS; Power BI; scikit-learn; Jupyter

`evaluate.py` maps these onto O*NET names (SQL -> "Structured query language SQL").
Check which names it could not map: fix typos, leave real out-of-vocabulary tools as they are.

    uv run python evaluation/evaluate.py --check evaluation/labels_<yourname>.csv

`notes`: anything unsure ("'Spark' could be the company name here").

## Agreement (two labellers)

Both of us label the same **postings** independently (don't discuss them first), then:

    uv run python evaluation/evaluate.py --agreement evaluation/labels_A.csv evaluation/labels_B.csv

Afterwards we discuss the disagreements and write one agreed file `evaluation/labels_gold.csv`,
which is what the evaluation uses. The agreement numbers go in the report.

### Agreement result:


40 items labelled by both
positive agreement (F1 between labellers): 0.86
Cohen's kappa over item x vocabulary decisions: 0.90 (inflated by the many easy 'not mentioned' decisions; report F1 first)

Disagreements (discuss, then write labels_gold.csv):
  post_003: only A: NoSQL | only B: -
  post_005: only A: - | only B: R, pandas
  post_006: only A: - | only B: Actimize, Oracle Mantas
  post_007: only A: OMOP CDM | only B: Epic Clarity
  post_008: only A: EC2, NoSQL, S3 | only B: Amazon EC2, Amazon S3
  post_010: only A: GCP, Kinesis | only B: Amazon Kinesis, Dataiku, Google, Microsoft Office, Snowflake, Tableau
  post_013: only A: JSON, NoSQL, XML | only B: -
  post_015: only A: - | only B: AWS, Amazon EMR, PyTorch, Spark
  post_016: only A: - | only B: Bash, Perl
  post_017: only A: - | only B: Power Automate
  post_019: only A: - | only B: Git
  post_021: only A: - | only B: Grafana, Microsoft Office, Power BI, Tableau
  post_022: only A: Glue, Lambda, S3, SageMaker | only B: Amazon S3, Amazon SageMaker, Hive, Spark
  post_023: only A: - | only B: Confluence, GitHub
  post_024: only A: - | only B: Python, SAS
  post_026: only A: - | only B: LangChain, LlamaIndex, PyTorch, TensorFlow
  post_028: only A: - | only B: Looker, Tableau
  post_029: only A: - | only B: Excel, Microsoft Office, PowerPoint, SQL
  post_030: only A: Google | only B: Dialogflow, HDFS
  post_031: only A: - | only B: DAX
  post_032: only A: - | only B: Git
  post_035: only A: - | only B: Looker, Tableau
  post_036: only A: - | only B: SAS, SPSS, Statistica
  post_038: only A: UiPath Orchestrator | only B: Power Automate

## Running the evaluation (in this order)

1. **Label the 10 dev postings**, then check the names (see Format above).
2. **Dev numbers, to look and debug.** Use your own label file and the dev split. `--errors` lists
   every false positive and miss, with the word that fired:

       uv run python evaluation/evaluate.py evaluation/labels_<yourname>.csv --split dev --matcher full exact vendor acronym
       uv run python evaluation/evaluate.py evaluation/labels_<yourname>.csv --split dev --matcher full --errors

3. **Both label the test postings**, then agreement, then `labels_gold.csv` (see Agreement above).
4. **The ablation on the test split (report this once).** Every normalisation step is compared
   against the full keyword matcher on the same postings:

       uv run python evaluation/evaluate.py evaluation/labels_gold.csv --matcher full exact vendor acronym

5. **Week 9: the main result.** The LLM and the hybrid compared against the keyword matcher.
   `<llm>` and `<hybrid>` are placeholders until `skillradar/llm_matcher.py` exists:

       uv run python evaluation/evaluate.py evaluation/labels_gold.csv --matcher full <llm> <hybrid> --baseline full

### How to read the output

- **Main table:** precision, recall and F1 per matcher, each with a 95% interval (bootstrap over items).
  "recall (all)" also counts out-of-vocabulary tools as missed.
- **Paired table:** each matcher minus the baseline, on the same postings. If the interval of
  **ΔF1 excludes 0**, the difference is real on this kind of data, even when the separate intervals
  in the main table overlap. "items better / worse / same" counts on how many postings the matcher
  makes fewer or more mistakes than the baseline.

### Rules that keep the evaluation honest

- **Dev is for looking, test is for reporting.** Do not open the matcher's output on the 30 test
  postings until `labels_gold.csv` is finished. Then run the test split and report that number.
- **Do not change the matcher after seeing test results.** The evaluated version is the tag
  `matcher-v1-frozen`. If the dev set shows a bug worth fixing, fix it *before* labelling the test
  set, add a test case, rebuild, and make a new tag (`matcher-v2-frozen`).