# 3. Results — IYQPIS

[Demo](demo.md) → [Code walkthrough](code-walkthrough.md) → **Results**

## Newly executed local review — 2026-10-14

The notebook recomputed historical aggregate arithmetic: **208/320 = 65.00% recall**, **122/1,576 = 7.74% false alerts/all records**, **112 missed anomalies**, **1,134 correct normal decisions**, and **330 total alerts**. All confusion counts reconcile to 1,576 records. This is new execution of a recorded-evidence review, not new prediction or test-population evidence.

Focused checks: `PYTHONPATH=src python -m pytest -q tests/test_lenze.py tests/test_lenze_baseline.py tests/test_lenze_verification.py` — **11 passed**. These tests use their own fixtures; no benchmark model was retrained for presentation.

Inspect [code and saved outputs](../notebooks/01_recorded_benchmark_review.ipynb). Source baseline: `c5de3f2857ca7f755e10cdf40147699da04c78f8`. The notebooks print exact source/evidence hashes; this delivery commit versions the notebook itself. [Recorded local environment](review-environment.json) identifies package versions; it is an observation, not a complete cross-platform dependency lock.

Local execution used sequential IPython cells in a fresh Python process because this environment disallows Jupyter socket transport. Standard `nbclient` fresh-kernel execution is configured in CI via `python scripts/execute_notebooks.py`; a local kernel run could not complete. HTML export succeeded. The saved error-analysis chart was visually inspected. A browser-rendered inspection of the complete notebook remains open because no local browser binary was available.

The local source snapshot was partial. Full repository validation and clean-run dependency checks are assigned to the GitHub workflow; see the actual workflow result on the pull request rather than inferring a pass from focused tests. No cloud verification was performed in this increment.

## Historical measurements remain authoritative

| Measurement | Result and interpretation |
|---|---|
| [MEAS-IYQPIS-001](../governance/measurements/MEAS-IYQPIS-001.md) | Recorded Lenze recall 208/320; point estimate 65%. Weak labels and precomputed features limit generalization. |
| [MEAS-IYQPIS-002](../governance/measurements/MEAS-IYQPIS-002.md) | 122 false alerts / 1,576 total records = 7.74%; this is not false positives / healthy rows. |
| [MEAS-IYQPIS-003](../governance/measurements/MEAS-IYQPIS-003.md) | 1,576/1,576 frozen binary decisions agreed across recorded runtimes; same population, not a new test. |
| [MEAS-IYQPIS-004](../governance/measurements/MEAS-IYQPIS-004.md) | 1,104,500 historically reported validated sample records; full source manifest/log provenance remains outside Git. |
| [Open KPI plans](../governance/measurements/planned-kpis.md) | Customer yield, scrap and intervention benefits remain not measured. |

## Remaining engineering and delivery work

Owner: Dr. Douglas Moore. Preserve the existing qualification backlog and release disposition. Raw-data EDA and new baseline/candidate comparisons need their actual source inputs and a defined evaluation protocol; this notebook does not substitute for them. Verified MLflow experiment/registry run links remain open and no tracking run was created here. Full notebook browser inspection, complete environment reproducibility and repository-level security/review-control verification are not established by this increment. CI changes cover bounded notebook execution and review-document links; they do not establish comprehensive security scanning.
