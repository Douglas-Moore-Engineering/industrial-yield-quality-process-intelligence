# Verification and validation

Tests will cover data contracts, transformations, model V&V, integration, security boundaries, rollback, degraded mode, and acceptance criteria.

Current coverage: [test_contracts.py](test_contracts.py) (contract validation library), [test_timestamps.py](test_timestamps.py) (timestamp integrity checks), [test_adapter_manufacturing_spc.py](test_adapter_manufacturing_spc.py) (first dataset adapter, including the documented Bearing Race Width drift and Shaft Diameter in-control cases). Run with `python -m pytest -q` after `pip install -r ../requirements-dev.txt`.

Data coverage now includes all five adapters, atomic batch publication/replay, checksums, rejected invalid/duplicate records, BAD-value aggregation exclusion, private-DNS checks, safe blob paths, and manifest-last Azure publication. Run `python -m pytest -q`; install `requirements-dev.txt` first. `infra/azure/Test-DataJobGuards.ps1` checks operator approval, region normalization, complete execution overrides and active-execution refusal without Azure access. See the [data runbook](../runbooks/data-engineering.md) for successful live Azure full-data/replay acceptance and its remaining production limitations.

`test_intelligence.py` adds temporal split/leakage checks, missing/nonfinite/stale/domain/envelope refusals, calibration metrics, model tampering refusal, shadow-only activation, rollback, mutually exclusive human decisions, audit-chain modification detection, drift/SPC checks, past-only retrieval, genealogy-cycle refusal and production-gate refusal. The full suite has 64 passing tests. This is reference software evidence, not plant acceptance or proof of predictive usefulness.

The current suite has 73 passing tests after adding `test_model_development.py`: fixed false-alert-budget/tie handling, forward folds, abstentions counted as missed failures, frozen-candidate eligibility, confirmation schema checks, exact-row overlap rejection, single-evaluation reservation and unchanged threshold verification. See [model acceptance](../runbooks/model-acceptance.md) for the pending independent data check.
