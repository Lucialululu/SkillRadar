scoring=lenient · split=test · 30 items (30 postings, 0 CVs) · 204 labelled tools, 47 out of vocabulary (23%)

| matcher | side | items | precision | recall (vocab) | recall (all) | F1 | F1 (all) | TP | FP | FN vocab | FN OOV |
|---|---|---|---|---|---|---|---|---|---|---|---|
| full | all | 30 | 0.97 (0.95–0.99) | 0.94 (0.90–0.98) | 0.73 (0.64–0.81) | 0.96 (0.93–0.98) | 0.83 (0.78–0.88) | 148 | 4 | 9 | 47 |
| skillradar.llm_matcher:LLMOnly | all | 30 | 0.98 (0.97–1.00) | 0.96 (0.92–0.98) | 0.92 (0.88–0.96) | 0.97 (0.95–0.99) | 0.95 (0.93–0.97) | 188 | 3 | 7 | 9 |
| skillradar.llm_matcher:Hybrid | all | 30 | 0.97 (0.95–0.99) | 0.97 (0.95–0.99) | 0.95 (0.92–0.97) | 0.97 (0.95–0.99) | 0.96 (0.94–0.98) | 193 | 6 | 4 | 7 |
| skillradar.llm_matcher:HybridVerify | all | 30 | 0.98 (0.96–1.00) | 0.94 (0.90–0.98) | 0.73 (0.64–0.81) | 0.96 (0.94–0.98) | 0.83 (0.78–0.89) | 148 | 3 | 9 | 47 |

Paired comparison against 'full' (bootstrap over items, both matchers scored on the same resample; an interval that excludes 0 means a real difference on this kind of data)

| compared | side | items | ΔF1 (95% CI) | p | Δprecision | Δrecall (vocab) | Δrecall (all) | items better / worse / same |
|---|---|---|---|---|---|---|---|---|
| skillradar.llm_matcher:LLMOnly − full | all | 30 | +0.01 (-0.01 to +0.04) | 0.343 | +0.01 (-0.01 to +0.04) | +0.01 (-0.03 to +0.05) | +0.20 (+0.12 to +0.27) | 7 / 5 / 18 |
| skillradar.llm_matcher:Hybrid − full | all | 30 | +0.01 (-0.00 to +0.03) | 0.099 | -0.00 (-0.02 to +0.02) | +0.03 (+0.01 to +0.06) | +0.22 (+0.15 to +0.29) | 4 / 2 / 24 |
| skillradar.llm_matcher:HybridVerify − full | all | 30 | +0.00 (+0.00 to +0.01) | 0.746 | +0.01 (+0.00 to +0.02) | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) | 1 / 0 / 29 |

LLM cost and behaviour (seconds and tokens are from the original API calls, also when cached)

| matcher | texts | api_calls | cached | input_tokens | output_tokens | seconds | dropped_ungrounded | grounded_by_name | rejected_candidates | linked_alias | linked_embedding | kept_oov | seconds per text |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| skillradar.llm_matcher:LLMOnly | 30 | 0 | 30 | 86242 | 5306 | 649.2 | 0 | 1 | 0 | 151 | 0 | 41 | 21.64 |
| skillradar.llm_matcher:Hybrid | 30 | 0 | 30 | 101549 | 7204 | 530.4 | 1 | 1 | 1 | 8 | 0 | 42 | 17.68 |
| skillradar.llm_matcher:HybridVerify | 30 | 0 | 30 | 101549 | 7204 | 530.4 | 0 | 0 | 1 | 0 | 0 | 0 | 17.68 |
