# 1. Demonstration — IYQPIS

[README](../README.md) → **Demo** → [Code walkthrough](code-walkthrough.md) → [Results](results.md)

Recompute recorded benchmark counts and render error analysis without loading a model.

## Start here

Use Python 3.12 or newer in an isolated environment. From the repository root:

```sh
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-notebooks.txt
python scripts/execute_notebooks.py
```

Open [the executed notebook](../notebooks/01_recorded_benchmark_review.ipynb) in GitHub or the repository's VS Code workspace. Run cells top-to-bottom to reproduce the visible outputs. The script starts a fresh kernel, fails on unexpected errors and saves outputs back to the notebook. Dependency installation needs package access; notebook execution uses local inputs. Allow approximately 1–2 minutes after installation on a laptop (planning estimate, not a capacity result).

## What is reproducible here

The notebook reads `.azure/lenze-acceptance.json` and `.azure/lenze-decision-consistency.json`, prints their hashes, recomputes ratios and confusion counts, and displays one chart. No cloud account, model download or training is needed. Outputs are retained in the notebook; no large artifacts are created.

## Full inference replay prerequisites

Full prediction replay is separate and remains unexecuted by this demonstration. It needs `Meta_Data.csv`, `Original_Features.csv`, `model.joblib` and `freeze.json` from the trusted recorded run, with an independently verified freeze hash. Repository owner Dr. Douglas Moore maintains these artifacts outside Git. Install `requirements-ml.txt` and follow the [frozen verification runbook](../runbooks/lenze-azure-verification.md). Never substitute an arbitrary serialized model or rerun `lenze.run()` just to recreate a display: that function fits a new model.

The notebook is a self-contained **recorded-evidence review**, not a self-contained inference demo. Upstream feature extraction and raw process-history EDA are not reproduced.
