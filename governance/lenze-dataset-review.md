# Lenze-QI intake review

## Completed local benchmark

The fixed [protocol](lenze-protocol.json) was implemented in `src/iyqpis/lenze.py` before test scoring. The model uses 16 non-optimized features; all six `*_opt` features are excluded because their fitting provenance is not independently verified. Training-only variant grouping assigns 3,343 normal rows to fitting and 852 to calibration. The 95th-percentile calibration cutoff was persisted with the model checksum before evaluating test outcomes.

On all 1,576 publisher test records, the model detects 208 of 320 anomalies (65% recall), with 122 false alerts (7.74% of all rows). Both fixed point-estimate criteria pass; ROC AUC is 0.88555. No test-driven adjustment or removal of weak-label cases was performed. This is local reference evidence; no Azure deployment or customer production acceptance is implied. The model and freeze are in ignored `artifacts/lenze/v1/`, with shareable evidence in `.azure/lenze-acceptance.json`. Test outcomes are now inspected and must not be reused for selecting improvements under a fresh-confirmation claim.

Reviewed 2026-09-28. User supplied three concatenated URLs, resolved to `Meta_Data.csv`, `Original_Features.csv` and `Quick_Start_Script.ipynb` from https://zenodo.org/records/13854459.

All three downloads match publisher MD5 values respectively: `ed5247187af7ce719f4885ce826f720b`, `f50a97d32e61413a9cb5f448301d8da8`, `fc48cfc72a97a2e768a63530d9a7bf82`. Files reside in ignored `artifacts/dataset-review/lenze/`. Notebook source was read as text, not executed. The 11.5 GB audio archive was not needed for this feature-table intake.

## Verified structural checks

- Metadata and feature tables each contain 5,771 unique `number` identifiers, with exactly matching identifier sets.
- There are 22 numeric feature columns; all values parse and are finite.
- The publisher assigns 4,195 training records and 1,576 test records. Preserve these assignments, joining by identifier rather than relying on row order.
- All training `class_label` values are `normal`. Training `quality_label` values include 0 (3,497 rows) and 1 (698 rows); therefore do not assume quality_label 1 means anomalous or defective. Resolve label semantics before evaluation.
- There are 350 training variants and 529 test variants, including 179 shared variants. The publisher split is not wholly a test of unseen variants.

## Modeling decision

Suitable for a separate geared-motor anomaly-detection reference benchmark using existing feature tables. This is not confirmation of the frozen SECOM model or the milling model. The publisher notebook demonstrates Isolation Forest on these features. Its published AUC is external evidence, not a result reproduced here and not evidence that our fixed recall/false-alert targets pass.

Before final evaluation: verify label semantics and provenance of the precomputed features (especially optimized/distance features); define score direction; reserve calibration data from the training partition; freeze preprocessing, model, cutoff and evaluation protocol. Never use `number`, `dataset`, `class_label`, `quality_label` or `perceived_category` as model predictors. Keep test labels out of selection and calibration. Training on normal examples requires a protocol suited to anomaly detection rather than supervised failure classification.

No test-label metrics, model fitting or Azure job were run during intake. Test feature finiteness and variant membership were inspected structurally, so this is a reserved benchmark test partition, not a claim of completely uninspected data. Customer production readiness remains outside this reference benchmark.
