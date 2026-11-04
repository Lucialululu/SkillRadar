scoring=strict · split=test · 30 items (30 postings, 0 CVs) · 204 labelled tools, 47 out of vocabulary (23%)

| matcher | side | items | precision | recall (vocab) | recall (all) | F1 | F1 (all) | TP | FP | FN vocab | FN OOV |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exact | all | 30 | 0.96 (0.91–0.99) | 0.56 (0.50–0.62) | 0.43 (0.36–0.51) | 0.71 (0.65–0.75) | 0.59 (0.52–0.66) | 88 | 4 | 69 | 47 |
| vendor | all | 30 | 0.94 (0.89–0.98) | 0.76 (0.71–0.81) | 0.59 (0.50–0.67) | 0.85 (0.80–0.88) | 0.73 (0.66–0.79) | 120 | 7 | 37 | 47 |
| acronym | all | 30 | 0.95 (0.90–0.98) | 0.95 (0.91–0.99) | 0.73 (0.65–0.82) | 0.95 (0.92–0.98) | 0.83 (0.77–0.88) | 149 | 8 | 8 | 47 |
| full | all | 30 | 0.97 (0.95–0.99) | 0.94 (0.90–0.98) | 0.73 (0.64–0.81) | 0.96 (0.93–0.98) | 0.83 (0.78–0.88) | 148 | 4 | 9 | 47 |

Paired comparison against 'exact' (bootstrap over items, both matchers scored on the same resample; an interval that excludes 0 means a real difference on this kind of data)

| compared | side | items | ΔF1 (95% CI) | p | Δprecision | Δrecall (vocab) | Δrecall (all) | items better / worse / same |
|---|---|---|---|---|---|---|---|---|
| vendor − exact | all | 30 | +0.14 (+0.10 to +0.18) | 0.000 | -0.01 (-0.03 to +0.01) | +0.20 (+0.15 to +0.26) | +0.16 (+0.11 to +0.20) | 17 / 0 / 13 |
| acronym − exact | all | 30 | +0.24 (+0.19 to +0.29) | 0.000 | -0.01 (-0.03 to +0.01) | +0.39 (+0.33 to +0.45) | +0.30 (+0.25 to +0.35) | 26 / 0 / 4 |
| full − exact | all | 30 | +0.25 (+0.20 to +0.30) | 0.000 | +0.02 (-0.01 to +0.05) | +0.38 (+0.31 to +0.45) | +0.29 (+0.24 to +0.35) | 27 / 0 / 3 |
