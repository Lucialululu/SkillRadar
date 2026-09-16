SkillRadar: A CV-to-job-market skill-gap tool for job-seeking students

02830 Advanced Project in Digital Media Engineering

Group size: 3

### **PROJECT IDEA**

Using large, publicly available job-posting datasets (with extracted required
skills, timestamped over multiple years) and an established open skills
taxonomy (O*NET, US Dept. of Labor - occupations mapped to required skills
and skill categories), we build a tool that lets a student upload or paste
their CV, extracts their current skills, compares them against the skills
most in demand for their target role/industry right now (and how that
demand has shifted over time), and returns a personalized "skill gap"
report: which skills to prioritize learning next, and evidence for why.

This keeps data gathering deliberately simple: no scraping, no live
web-navigation, no fragile HTML parsing, no waiting for data to accumulate.
Both data sources are static, downloadable, well-documented datasets
intended for exactly this kind of analysis - the entire historical dataset
is available on day one.

### **MOTIVATION (why and who would care about this project)**

Every DTU student job-hunting for an internship, student job, or first
graduate role faces the same problem: it's hard to know, in concrete terms,
which skills actually matter for the roles they want, whether their CV
reflects what employers are currently asking for, and which skill gaps are
worth closing before an application deadline. Existing tools (LinkedIn
"skill match", generic CV checkers) either require a paid account, only
compare against a single job posting at a time, or give vague/generic
advice rather than a structured, evidence-based view of what is trending.
A tool that turns a large body of real job-posting data into a personal,
concrete recommendation is directly useful to a huge, relatable population
of students - and to us as users ourselves during and after this course.

Target audience: DTU students and recent graduates applying for jobs and
internships; more broadly, any job-seeker trying to prioritize what to
learn next.

### **PROJECT GOALS**

1. Build a model/pipeline that extracts skills from free-text CVs and
 matches them against a structured skill taxonomy, so a CV can be
 represented as a comparable skill vector.

2. Identify which skills are most in demand for a given role/industry
 right now, and how that demand has shifted over a recent time window,
 using historical job-posting data.
 
3. Build a lightweight tool/interface where a user uploads a CV and a
 target role, and gets a simple, personalized recommendation ("you're
 missing X and Y, which appear in Z% of postings for this role and are
 trending up/down over the last N months").

Stretch goal (only if time allows): let the tool suggest a short learning
path (e.g. specific course/resource type) per missing skill, not just
identify the gap.

### **DELIMITATION (what is explicitly out of scope)**

- No job-application automation or auto-generated cover letters - we predict/compare skills, we do not apply on the user's behalf.

- No salary prediction or negotiation advice - scoped strictly to skill-demand matching.

- No guarantee of hiring outcomes - the tool reports what the data shows
 about skill demand, not whether a specific person will get a specific job.

- No mobile app - a simple web-based prototype is sufficient to test the goal.

### **TESTING**

1. Quantitative: backtest skill-demand predictions against a held-out,
 more recent slice of postings - does what we flagged as "trending"
 actually show up more often in the held-out period than in a naive
 baseline (e.g. "demand stays constant")?

2. Feature-value test: ablation - does removing the taxonomy-based skill
 normalization (O*NET) meaningfully hurt CV-to-posting matching accuracy
 compared to raw keyword matching? This directly answers our second
 project goal and gives us a real design finding to report.

3. Human-centered: small peer trial - give classmates who are actively
 job-hunting access to the tool, ask them to try it with their real CV,
 then ask whether the identified gaps felt accurate/useful and whether
 they'd trust/use it going forward.

### **RISKS (tackle the hard + essential problem first, per the playbook)**

- CV parsing from free text (PDF/Word) is noisy - skill extraction quality
 directly limits everything downstream.
 **ACTION:** build and test the CV-to-skills extraction step first, in week
 1-2, on our own CVs, before building anything else - this is our tracer
 bullet through the riskiest part of the project.

- Job-postings datasets are third-party/scraped, not official government
 data, so licensing, quality, and consistency need to be checked early.
 **ACTION:** confirm license terms and inspect data quality (missing fields,
 duplicate postings, inconsistent skill tagging) in week 1, and have a
 backup dataset identified in case the first choice is unusable.

- O*NET is US-focused, which may not map cleanly onto the Danish/European
 job market or DTU students' target roles.
 **ACTION:** check coverage against a handful of real DTU-relevant job ads in
 week 1-2; if mapping is poor, fall back to a data-driven skill list built
 directly from the job-postings dataset instead of relying on O*NET.

- "Skill demand" is a fuzzy, contestable concept - our definition and
 metric need to be precise enough to test, not just plausible-sounding.
 **ACTION:** nail down a concrete, quantifiable definition of "trending skill"
 in week 2-3, before building the trend model.

### **SUGGESTED WORK SPLIT (for a 3-person group with limited hours/week)**

- Person A - Data pipeline: source and clean the job-postings dataset,
 integrate the O*NET taxonomy (or build a fallback), structure the
 combined dataset for downstream use.

- Person B - Model/analysis: build the CV skill-extraction and matching
 model, run the trend/backtest and ablation study, write up the state-of
 -the-art literature on skill extraction and labor-market analytics.

- Person C - Prototype + testing: build the simple web interface (CV
 upload -> skill-gap report), recruit and run the peer trial, collect and
 summarize feedback.

All three threads can start in parallel from week 2 onward once the
dataset and taxonomy are confirmed usable, which matters given limited
weekly hours - no one should be blocked waiting on another part for long.

### **ROUGH WEEK-BY-WEEK PLAN (realistic for part-time-job schedules)**

Week 1-2:
Source the job-postings dataset and O*NET taxonomy, check
license/quality/coverage for Danish/EU relevance.
Build a first CV-to-skills extraction pass on our own CVs.
Draft motivation/goals/scenario for lightning presentation.

Week 3:
Lightning presentation: project idea and motivation.
Tracer bullet - one CV, one target role, one naive skill-gap
report, end-to-end.

Week 4-5:
Pre-mortem / risk assessment presentation.
Nail down the "trending skill" metric definition.
Start literature review on skill extraction and labor-market
analytics methods.

Week 6-8:
Build out the real skill-matching and trend model.
Start building the interface in parallel.
Explore the learning-path stretch goal if time allows.

Week 9-10:
Run the backtest and ablation study.
Recruit peers who are actively job-hunting and start the human
trial (needs 1-2 weeks of real usage, so start this with margin
before the deadline).

Week 11-12:
Finish peer trial, collect results.
Write the report (max 4 pages for a 3-person group).
Prepare final presentation.

Week 13: Project hand-in. Course evaluation.

### **LINKS**

**Kaggle datasets:**
1.3M LinkedIn jobs with skills (2024): https://www.kaggle.com/datasets/asaniczka/1-3m-linkedin-jobs-and-skills-2024
LinkedIn Job Postings 2023–2024 (larger, more metadata): https://www.kaggle.com/datasets/arshkon/linkedin-job-postings

**O*NET:**
Web Services API: https://services.onetcenter.org/
Documentation: https://services.onetcenter.org/reference/
Free registration required: https://services.onetcenter.org/developer/signup