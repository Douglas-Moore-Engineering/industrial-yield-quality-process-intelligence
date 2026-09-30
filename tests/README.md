# Verification and validation

## Contents

- [Recorded execution and current scope](#recorded-execution-and-current-scope)
- [Test groups](#test-groups)
- [Run locally](#run-locally)
- [Requirements and evidence](#requirements-and-evidence)

## Recorded execution and current scope

The latest retained reference replay record at the reviewed baseline reports **90 local software tests passed**, alongside successful Azure execution on 2026-09-29 UTC. See [results](../docs/azure-validation-results.md) and [machine-readable evidence](../.azure/github-validation-result.json). Earlier 64/73/77/86-test statements describe historical increments, not competing current results. This index correction does not claim a fresh run of that suite.

Test definitions verify bounded software behavior. They do not establish plant acceptance, predictive usefulness at a customer, an independent assessment, or completion of cloud operational assurance.

## Test groups

| Group | Definition | Scope |
|---|---|---|
| Contracts/time | [contracts](test_contracts.py); [timestamps](test_timestamps.py) | Record fields, types, time formatting, ordering and duplicates |
| Sample adapters | [AI4I](test_adapter_ai4i_2020.py); [Bosch](test_adapter_bosch_injector_eol.py); [SPC](test_adapter_manufacturing_spc.py); [SECOM](test_adapter_secom.py); [steel](test_adapter_steel_plates_faults.py) | Source-specific sample semantics; explicit missing/unknown values |
| Batch publication | [pipeline](test_pipeline.py); [Azure adapter](test_azure_batch.py) | Atomic publication, replay, source/artifact checks, private-DNS and path guards; mocked remote calls are not live Azure tests |
| General reference intelligence | [intelligence](test_intelligence.py) | Temporal splits, preprocessing, shadow abstention, ledger, reference rollback, supplied-edge genealogy and production refusal |
| Candidate development | [model development](test_model_development.py) | Forward folds, alert budget, abstention accounting, confirmation eligibility/overlap and fixed thresholds |
| Lenze reference | [metrics](test_lenze.py); [baseline](test_lenze_baseline.py); [verification](test_lenze_verification.py) | Fixed decision rule/denominator, training-only profile, record-level digest and freeze-tampering refusal |
| Monitoring | [monitoring](test_monitoring.py) | Input validation, review signals and labeled performance; no paging-delivery proof |
| Milling intake | [milling](test_milling_audit.py) | Group assignment and malformed input checks; not model acceptance |

The [local Lenze recovery drill](../src/iyqpis/lenze_recovery.py) has separate [recorded evidence](../.azure/lenze-recovery-evidence.json); its eight cases are not eight additional pytest results or cloud restore evidence. Platform guard scripts under `infra/azure/` likewise have their own scope and execution records.

## Run locally

From the repository root, in an isolated environment compatible with the dependency files:

```bash
python -m pip install -r requirements-dev.txt -r requirements-data.txt -r requirements-ml.txt
python -m pytest -q
```

Keep the checked-in sample inputs available for adapter tests. Do not interpret a reproduced software test result as a new evaluation of the frozen publisher test partition. Cloud commands are separate, may incur charges, and require their documented execution context.

## Requirements and evidence

Use the [50-row verification matrix](../requirements/verification_matrix.csv) to distinguish test definitions, historical execution evidence and remaining acceptance. A reference shadow guard does not automatically apply to the Lenze batch entry point. The [review](../governance/reviews/2026-09-30-reference-review.md) records the documentation correction and validation limits.
