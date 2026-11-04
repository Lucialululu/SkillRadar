scoring=lenient · split=test · 4 items (0 postings, 4 CVs) · 61 labelled tools, 14 out of vocabulary (23%)

| matcher | side | items | precision | recall (vocab) | recall (all) | F1 | F1 (all) | TP | FP | FN vocab | FN OOV |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exact | all | 4 | 0.95 (0.87–1.00) | 0.89 (0.83–0.97) | 0.69 (0.62–0.79) | 0.92 (0.88–0.97) | 0.80 (0.72–0.88) | 42 | 2 | 5 | 14 |
| vendor | all | 4 | 0.96 (0.87–1.00) | 0.96 (0.93–1.00) | 0.74 (0.63–0.86) | 0.96 (0.90–1.00) | 0.83 (0.74–0.92) | 45 | 2 | 2 | 14 |
| acronym | all | 4 | 0.96 (0.88–1.00) | 1.00 (1.00–1.00) | 0.77 (0.69–0.88) | 0.98 (0.94–1.00) | 0.85 (0.78–0.93) | 47 | 2 | 0 | 14 |
| full | all | 4 | 0.96 (0.88–1.00) | 1.00 (1.00–1.00) | 0.77 (0.69–0.88) | 0.98 (0.94–1.00) | 0.85 (0.78–0.93) | 47 | 2 | 0 | 14 |

Paired comparison against 'exact' (bootstrap over items, both matchers scored on the same resample; an interval that excludes 0 means a real difference on this kind of data)

| compared | side | items | ΔF1 (95% CI) | p | Δprecision | Δrecall (vocab) | Δrecall (all) | items better / worse / same |
|---|---|---|---|---|---|---|---|---|
| vendor − exact | all | 4 | +0.03 (+0.00 to +0.06) | 0.120 | +0.00 (+0.00 to +0.01) | +0.06 (+0.00 to +0.11) | +0.05 (+0.00 to +0.09) | 2 / 0 / 2 |
| acronym − exact | all | 4 | +0.06 (+0.01 to +0.09) | 0.004 | +0.00 (+0.00 to +0.01) | +0.11 (+0.03 to +0.17) | +0.08 (+0.02 to +0.13) | 3 / 0 / 1 |
| full − exact | all | 4 | +0.06 (+0.01 to +0.09) | 0.004 | +0.00 (+0.00 to +0.01) | +0.11 (+0.03 to +0.17) | +0.08 (+0.02 to +0.13) | 3 / 0 / 1 |
