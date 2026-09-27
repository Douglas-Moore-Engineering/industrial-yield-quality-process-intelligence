# Model Validation, V&V and Trustworthiness

## Required evidence

| Validation area | Required evidence |
|---|---|
| Temporal validity | time-based train/validation/test separation; no future leakage |
| Group validity | hold out runs/lots/assets when testing generalization |
| Calibration | reliability assessment and Brier/ECE where probabilistic risk is used |
| Imbalance | PR-AUC, recall at alert budget, false alerts per shift |
| Warning horizon | useful lead time before irreversible quality disposition |
| Robustness | missing sensors, noise, stale data, substitutions, changeovers |
| Domain shift | detect new machine/recipe/material distributions and abstain/restrict authority |
| Explainability | stable engineering-useful attribution; not presented as proof of causation |
| Causal claims | domain review, sensitivity analysis and explicit assumptions |
| Digital twin | verification, validation and uncertainty quantification before prescriptive use |
| Human factors | usability, comprehension, actionability and acknowledgment testing |
| Rollback | return to prior approved model/configuration without plant interruption |

## Trustworthiness rule

A model is not promoted because it achieves a single favorable metric. Promotion requires the agreed evidence package and release-gate exit criteria.
