# 2. Code walkthrough — IYQPIS

[Demo](demo.md) → **Code walkthrough** → [Results](results.md)

## Frozen Lenze benchmark: actual execution order

| Order | Actual code | Responsibility and output |
|---|---|---|
| 1 | [`lenze.py`: `run`](../src/iyqpis/lenze.py) | Reads metadata and precomputed-feature CSVs; checks unique matching identifiers, partition names and finite feature values. |
| 2 | [`lenze.py`: `calibration_variant`](../src/iyqpis/lenze.py) | Hashes variant IDs to separate normal training data into fitting and calibration groups. Publisher test records stay outside fitting. |
| 3 | [`lenze.py`: `run`](../src/iyqpis/lenze.py) | Fits Isolation Forest (500 estimators, max_samples=256, random_state=42); uses the 95th percentile of calibration anomaly scores with the `higher` method for the cutoff. |
| 4 | [`lenze.py`: `run`](../src/iyqpis/lenze.py) | Saves the model and freeze manifest with ordered features, cutoff, code and source hashes before test scoring. This is a training command, not a display command. |
| 5 | [`lenze.py`: `metrics`](../src/iyqpis/lenze.py) | Uses scores strictly greater than cutoff; computes recall, false alerts/all rows and ROC AUC; writes evaluation while production release remains blocked. |
| 6 | [`lenze_baseline.py`: `build`](../src/iyqpis/lenze_baseline.py) | Separately profiles publisher training rows, including calibration, against the frozen source hashes. Does not change the model or thresholds. |
| 7 | [`lenze_verification.py`: `verify`, `decision_digest`](../src/iyqpis/lenze_verification.py) | Verifies the externally supplied freeze hash and all source/model digests before loading the trusted artifact; checks records and reproduces a sorted binary decision digest. |
| 8 | [`azure_lenze.py`](../src/iyqpis/azure_lenze.py) | Provides the separate Azure entry path; operation and prerequisites are in the [verification runbook](../runbooks/lenze-azure-verification.md). |
| 9 | [`01_recorded_benchmark_review.ipynb`](../notebooks/01_recorded_benchmark_review.ipynb) | Reads saved acceptance/replay summaries, reconciles counts and displays error analysis. It does not execute steps 1–8. |

## Distinguish the other pipelines

[`pipeline.py`](../src/iyqpis/pipeline.py) and adapters implement the sample-data contract pipeline. [`intelligence.py`](../src/iyqpis/intelligence.py) and the [reference AI runbook](../runbooks/reference-ai.md) describe the earlier SECOM path; its failed confirmation results must not be presented as the passing Lenze benchmark. The [source index](../src/README.md) links both paths.

## What remains to build or verify

The Lenze feature profile is retrospective; upstream extraction, point-in-time availability and raw-process EDA remain unverified. Future baseline/candidate experiments must use a defined split and selection protocol before final evaluation. A feature catalog or local artifact ledger does not establish a production feature store or verified MLflow integration. No Decision Tree/XGBoost comparison or new MLflow run is claimed by this documentation increment.
