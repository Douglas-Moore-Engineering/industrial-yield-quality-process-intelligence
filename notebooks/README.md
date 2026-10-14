# Executed review notebooks

Read in this order: [Demo](../docs/demo.md) → [Code walkthrough](../docs/code-walkthrough.md) → [Results](../docs/results.md).

1. [01_recorded_benchmark_review.ipynb](01_recorded_benchmark_review.ipynb) — Recompute recorded benchmark counts and render error analysis without loading a model.

Install `requirements-notebooks.txt` and run `python scripts/execute_notebooks.py` from the repository root. Select the same Python environment in VS Code. Saved outputs make the work inspectable without running cells.

This is a bounded review notebook, not raw-data EDA or a newly trained model comparison. Those require the approved source inputs and evaluation protocol. Keep reusable behavior in `src/`; notebooks must not become production runtime dependencies. No MLflow tracking or registry integration is established by notebook execution.
