# **Risks**

### **Explain**

##### *What problem are you solving?*

POV: you are searching for a job in ML, and you have only used Python. But then, you see a job for ML engineering that requires C++ and Java. Is it worth to learn and pick up C++ and Java?

We want so solve this problem by:

- Collecting CV and job post data from LinkedIn and other job boards
- Compare your CV skills to a targeted job post requirement
- Give percentage match and suggestions on what skills to learn to increase the match
- Also give the trend of required skills: like I am missing C++ for this SINGULAR job post, but check if maybe more job posts in this field also needs C++? Then it might be clear that this is something to learn.
- Secondary problem we want to solve: problem of exact string keyword matching, but instead we map to a taxnonomy, so now we can match via synonyms. 
- Taxonomies are usually also hierarchical, so you can reason about *related* skills, not just identical ones (e.g. "PyTorch" and "TensorFlow" might both sit under a broader "deep learning frameworks" skill group, which is useful for a gap report that shows "close" skills, not just exact ones).

##### *What are you trying to achieve?*

- Achieve a tool that can show you missing skills and trends in the job market, so you can make a better decision on what to learn next.
- Help paint a picture of what is "worth it" to learn, because time is limited.

### **Fail**

Imagine it is week 13 and the project failed:

- What went wrong?
- We could note snapshot or adapt the chosen pre-trained model good enough for the "synonym" matching, and it did not outperform an already simple solution aka keyword matching.
- We could not define a good "mathematical" model for a way to "rank" relevant skills to learn, like should I really learn c++? And we could not answer this because our baseline definition of "relevant" was too fuzzy, aka we could not define a good metric for "relevance" and we could not find a good way to measure it.
- We did not have a good enough method for extracting skills from both job posts and CVs, they were too noisy and "different" in structure, and we could not find a good way to normalize them to a common taxonomy.

### **Act**

- What is the underlying risk?
- Mapping different CVs and job posts to a normalized taxonomy, so the main problems are the normalization of something that could be super "broad".
- Risk of how we fine tune and snap shot the pre-trained model, and what if we "tunnel vision" on one model too much, only to find out that it is not the best model for our use case? And there were better candidates out there that were never considered?

- What can you test, change, reduce, or clarify now?
- Test different pre-trained models for the synonym matching, and see which one performs best on a small sample of job posts and CVs.
- Test different methods for extracting skills from job posts and CVs, and see which one gives the most accurate and normalized results.

### **BY THE END OF THE WEEK**

– A clearer and smaller project scope. You should know what is essential and what can be postponed or removed.
- We should focus on the core functionality of showing percentage of match between CV and job post + showing the missing skills and trends in the job market. The secondary problem of exact string keyword matching can be postponed for now.

– A list of risks that could derail the project. Data access, technical feasibility, integration, user testing, evaluation, time, dependencies.
- Data access with O*NET and if the kaggle data set is good enough for our use case.
- Finding out which pre-trained model is the best suitable?
- Integration of the different components (data extraction, skill matching, trend analysis) and how they will work together.
- Extracting skills from job posts and CVs accurately and normalizing them to a common taxonomy.
- Finding enough CVs to test.

– A prioritized risk picture. Which risks are most likely? Which would be most damaging?
- Data access with O*NET and if the kaggle data set is good enough for our use case.
- Normalizing skills and be able to extract them accurately from job posts and CVs.
- Finding out which pre-trained model is the best suitable?

– Concrete actions for the biggest risks. Each major risk should lead to something you can test, investigate, decide, or change now.
- Quick baseline tests of O*NET and kaggle data sets.
- Testing of pre-trained models or dive deeper into them in theory to see what they are capable of.

– A more focused prototype plan. Your plan should reflect what you learned from the premortem.
- More scoped focus since we now weight skill matching and scoring higher than synonym matching.

– Tracer bullets underway. Start testing the assumptions that matter most instead of continuing to plan around them.
- ...

### SLIDES GUIDE (BRAINSTORM):
Slide 1: Project description, Motivation and Goals. This slide can simply be an updated version of the one you have already presented.

Slide 2: Your plan. This could be your Trello board or just the list of tasks that you believe you must complete to fulfill your goals. It is important that the plan is realistic and that it will plausibly lead to goal fulfillment.

Slide 3: Your risk assessment. This slide should contain the risks that your premortem unearthed and any other risks that you are aware of. The focus should be on risks that are specific to your project. 