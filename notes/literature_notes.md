### Literature relevant to hybrid LLM keyword matching + verification

**Prompt 1 from Claude:**

| Paper | What they did | How it relates to your hybrid |
|---|---|---|
| **Clavié & Soulié (2023)** | A cheap first step proposes candidate ESCO skills for a job-ad sentence; an LLM (GPT-4) then re-ranks them in context. It beat the previous best by a wide margin | **Closest to your design.** Your keyword matcher is the candidate step, and your LLM verifier is the context step. Cite it as the inspiration for the hybrid |
| **Nguyen et al. (2024)** | Few-shot LLMs for skill extraction, compared with trained (supervised) models on six datasets. LLMs were worse overall, but better on complex, ambiguous mentions | Explains why you let the LLM **verify** rather than extract alone, and predicts *where* it should help: ambiguous cases like "Go further", "excel at" or company names |
| **Zhang, van der Goot & Plank (2024), Entity linking** | Trained models link skill mentions in job ads to the ESCO taxonomy. Even the best got only ~24% exactly right | Shows that linking free text onto a *large* taxonomy is hard, which justifies your narrow, explicit list of ~300 tools |
| **SkillSpan (Zhang et al. 2022)** | A labelled dataset plus trained extraction models (domain-adapted BERT) for hard and soft skills | The standard trained approach. You chose not to train, for scope and data reasons; this is what you position against |

**How to compare your work with theirs, honestly:**

> **Compare designs and findings, not raw numbers.** They use different taxonomies (ESCO with ~14,000 skills vs. your 301 tools), different text (job-ad sentences vs. your full postings *and* CVs) and different metrics (ranking scores like RP@10 or Acc@1 vs. your precision/recall). Putting your F1 next to their RP@10 would be comparing apples and oranges, and examiners would notice.

> **What you *can* say:** "Following Clavié & Soulié, we use cheap candidate generation plus LLM verification. Unlike them, we target a small, explicit tool vocabulary and apply it to CVs. Consistent with Nguyen et al., we find (or don't find) that the LLM's gains come mainly from ambiguous mentions." That last part is something you can check in your error analysis, with `evaluate.py --errors`.

> **Your contribution, stated clearly:** they ask "can LLMs map skills well?" You ask "for explicit tool mentions in CVs and job ads, is adding context verification worth the extra cost, and how should a user stay in control of the result?" The second half, the human-in-the-loop correction, isn't in any of these papers. That's your human-centred angle.

**One optional extra:** the SkillSpan authors published a ready-trained extraction model (`jjzha/jobbert_skill_extraction` on Hugging Face). You could run it on your 30 labelled postings as a fourth method: "a published trained extractor". It finds skill phrases but doesn't map them to O*NET, so it would need your normaliser on top. It's a nice-to-have only if time allows, but it would let you say you compared against a real trained model from the literature.

**A caution:** so far I've only read these papers' abstracts and summary pages. Before you cite a specific claim, read the relevant section yourself. The week 8 literature lecture is right that a citation existing doesn't mean it supports your sentence.