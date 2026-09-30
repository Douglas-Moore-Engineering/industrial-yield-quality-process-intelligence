# Security and operational assurance implementation — 2026-09-30

Source baseline: `d82281ab90e96ca59ec8db6f7584ed3de52279c1`. Scope: user-authorized corrections to the pre-customer reference environment. Independent reviewer and organizational risk approver remain unassigned.

## Implemented changes

- [Scoped Checkov dispositions](../azure-ml-scan-disposition.md) based on pinned scanner source and Microsoft documentation, with compiled-template security checks and negative tests.
- CI compilation expanded to every top-level Bicep entrypoint.
- [Reference assurance tooling](../../infra/azure/reference_assurance.py) provides read-only monitoring observations, explicitly labeled diagnostic output and a disposable-container restore drill. Evidence is checkpointed before deletion; accepted artifacts cannot be targeted. See the [operational runbook](../../runbooks/reference-operational-assurance.md).

## Verification

Initial security commit `a02b7a5a1cea18c5dc00db6f57f503c199e33c32` passed [platform CI run 36751922591](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/actions/runs/36751922591): all top-level entrypoints compiled, five PowerShell guard scripts passed, eight compiled-security/private-probe tests passed, and Checkov reported **50 passed, 0 failed, 7 skipped**. Four of those skips are the newly documented resource-scoped dispositions; three pre-existed. This is not a claim that the skipped generic policies passed.

Combined implementation commit `6539d82bb6ec007be36a92d86a39beb07353164e` passed [platform CI run 36753201524](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/actions/runs/36753201524): **10 Bicep entrypoints**, the compiled security contract, **five PowerShell guard scripts**, and **21 Python security/operational tests** passed. Checkov again reported **50 passed, 0 failed, 7 skipped**. The Python tests comprise five compiled-configuration tests, four private-probe tests and 12 operational safety tests. The 12 operational tests also passed locally with simulated clients.

Readback of all 15 implementation files at that commit matched the prepared contents. Relative documentation links and assurance-register references were checked. Python model/data code, frozen thresholds and historical Azure evidence are unchanged; the earlier 90-test data-suite result is not relabeled as a new execution. The final documentation update records these results without changing the tested executable files.

## Cloud execution boundary

This session has GitHub repository/CI access but no Azure provider tool, Azure CLI installation or authenticated private Azure execution path. No cloud resource, role, networking setting, replication tier, notification recipient or model artifact has been changed. Live log ingestion, failure notification, cloud restore and production RPO/RTO remain unverified.
