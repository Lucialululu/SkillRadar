### **Project idea:**

A tool that extracts a CV's current skills, maps them onto a structured skill taxonomy, and compares them against aggregated job-postings data for a target role - currently scoped to the international tech job market, where open, structured data is richest - surfacing which skills are missing and whether demand for them is rising or falling.

### **Project motivation:**

Students and recent graduates often know which jobs they want, but not which skills employers currently value most, or which gaps are worth closing. Existing tools compare a CV against one posting at a time, or give generic advice. This tool instead aggregates job-market data into a personal, evidence-based picture of current demand.

**How it works:**
CV → extract & normalize skills → compare with job-postings data → rank missing skills by demand and trend

**Output example:**
Docker - missing - in 42% of postings - ↑ rising demand
Azure - missing - in 31% of postings - ↑ rising demand

# **SCRIPT:**


Imagine you're a student applying for your first data-science job. You know Python and machine learning - but you don't know which skills employers are currently asking for, or what you should learn next.

Our project takes a student's CV, extracts and normalizes their skills, and compares them against real job-postings data for a chosen role. Instead of comparing to just one vacancy, we aggregate many postings and look at both how common a skill is, and whether demand for it is rising or falling.

The result is a personalized skill-gap report. For example, it might tell you Docker is missing from your CV, appears in 42% of relevant postings, and is trending upward.

Technically, the core challenges are extracting skills reliably from free-text CVs, mapping them onto a consistent taxonomy, and defining a meaningful measure of how demand is changing. We will also test whether taxonomy-based matching actually performs better than simple keyword matching, which is one of the more interesting open questions in our design.

___

### Note: what "taxonomy-based matching" actually means

**Keyword matching** (the naive baseline):
Compare CV text and job posting text as raw strings. A skill only "matches" if the exact word or phrase appears in both.

- Problem: it misses synonyms and near-equivalents.
  - CV says "Amazon Web Services", posting says "AWS" → no match, even though they mean the same skill.
  - CV says "Docker", posting says "Docker containers" → no match.
  - CV says "Docker containers", posting says "containerization" → no match.
  - CV says "React.js", posting says "ReactJS" → depends on exact string handling, easy to miss.
- It also can't tell related skills apart from identical ones - "Python" and "Python 2" might get treated as totally unrelated tokens.

**Taxonomy-based matching** (the more structured approach):
Instead of comparing raw text to raw text, map *both* the CV skills and the posting's requested skills onto a shared, structured vocabulary (a taxonomy - e.g. ESCO or O*NET) *before* comparing them.

- Each skill in the taxonomy has one canonical ID, with known synonyms/aliases attached to it.
  - "AWS", "Amazon Web Services", "aws cloud" → all map to the same taxonomy skill ID.
- Comparison then happens on IDs, not strings - so synonyms and phrasing differences stop being a problem.
- Taxonomies are usually also hierarchical, so you can reason about *related* skills, not just identical ones (e.g. "PyTorch" and "TensorFlow" might both sit under a broader "deep learning frameworks" skill group, which is useful for a gap report that shows "close" skills, not just exact ones).

### Comments form external assistant:

**Why this is a genuine research question for the project, not just an implementation detail:**
Taxonomy-based matching sounds strictly better, but it isn't free:
- Free-text CVs and job postings are messy; mapping messy text onto a fixed taxonomy (an NLP problem called *entity linking* or *normalization*) can itself introduce errors - e.g. mapping "Java" the programming language to "Java" the island, or missing a skill entirely because it's phrased in a way the taxonomy mapper doesn't recognize.

- So the actual thing worth testing is: **does the added complexity of taxonomy mapping produce a measurably better skill-gap report than just doing simple keyword matching?** If taxonomy mapping is noisy or introduces its own errors, keyword matching (simpler, faster, easier to debug) might perform just as well or better in practice.

- This is exactly the kind of "is the added complexity worth it" ablation study the course wants to see - not just "we built the fancier version," but "we tested whether the fancier version was actually justified."