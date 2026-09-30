# Where we stand against the plan in slides

| Slide plan | Status |
|---|---|
| Week 3: check data quality and licensing | Done, including the notebooks and findings tables. Two license TODOs are still in the README. |
| Week 3: extract skills from our own CVs, "the riskiest step, tested first" | **Not done.** The matcher can now do it, but no CV has gone through it yet. |
| Week 4–5: lock the "trending skill" definition | **Not done.** We now know the data can't support a trend, but the slides still promise "rising or falling" and "trend direction". |
| Week 4–5: start the literature review | Not started. |
| Week 6–8: real matching model, trend metric, taxonomy matching, web prototype | Next week. The keyword matcher is ready to build on. |
| Week 9–10: backtest trend predictions vs a naive baseline | **Can't happen as planned**, since there's no time series. It needs a replacement test. |

# Next steps, in order

**[DONE] 1. Clean up the push (5 minutes).** Python cache files (`__pycache__/*.pyc`) and `.DS_Store` files were committed. Remove them and ignore them from now on:

```bash
printf "__pycache__/\n*.pyc\n.DS_Store\n.pytest_cache/\n" >> .gitignore
git rm -r --cached skillradar/__pycache__ tests/__pycache__ .DS_Store preprocessing/.DS_Store
git commit -m "ignore cache files"
```

**2. Make the notebooks use the new module.** Both notebooks still run their own old copy of the matcher. This matters most in the primary notebook's Section 4: the label side still calls the old `extract_tools` on the joined label string, which is exactly the lowercase bug. Replace the matcher cell with the import, switch the label line to `m.extract_tools_from_labels(...)`, and rerun Section 4. The "R, Spark, Scala, scikit-learn, Excel = 0% from labels" row in our findings table should then change to real agreement numbers. Run `m.suggest_drops(...)` once as well and fill in `MANUAL_DROP`.

**3. Shoot the tracer bullet, since it's still missing.** This is the one thing our slides, our premortem and our risk table all say comes first. Break it into three small modules and one command:

- **`cv_parser.py`:** turns a PDF into text, e.g. with `pdfplumber`.
- **`demand.py`:** computes "% of postings per tool" for a role. Run it once, offline, and save a small CSV per role (e.g. `data/processed/demand_data_scientist.csv`). The app should never have to stream the 5 GB `job_summary.csv`.
- **`report.py`:** compares the CV's tools with the demand table and ranks what's missing.
- **`main.py`:** ties them together as `python main.py my_cv.pdf "data scientist"`, printing the report.

Then run it on our three own CVs. Before running, write down by hand which skills each CV actually contains. That gives us our first real accuracy numbers for Goal 1, and we will see how CV text differs from posting text (bullet layouts, PDF artefacts, skills tucked into project descriptions).

**4. Decide Goal 2 this week and update the slides and docs.** our plan puts this in weeks 4–5, and the week 9–10 backtest depends on it. The realistic options are the ones from before:

- **Robust current demand:** % of postings plus the O*NET Hot Technology flag. We would test it by checking whether the skill rankings replicate across the two datasets (rank correlation of the top 20, with bootstrap confidence intervals). This directly replaces the backtest.
- **Entry-level vs senior:** which skills become more important with seniority. The secondary dataset has both levels.
- **An external time series** for the trend signal only, such as past O*NET releases or the yearly Stack Overflow survey. Only if one turns out to be usable.

Whatever we choose, change "rising or falling" and "trend direction" in the goal wording, `project_draft.md` and the README, so the whole project promises the same thing.

**5. Start a small hand-labelled evaluation set.** Mark the tools in 30–50 data-scientist postings by hand. That lets us measure precision and recall for the keyword matcher now, and it's the ground truth the week 9–10 keyword-vs-taxonomy study needs. Next week's lecture is on testing methods, so bring this and the Goal 2 test with our.

**6. Start the literature review, if someone has hours free.** Good starting points are SkillSpan (skill extraction from job postings, from ITU Copenhagen), JobBERT, and work on ESCO- or O*NET-based skill normalisation. These are also where our synonym/taxonomy matcher ideas for weeks 6–8 will come from.
