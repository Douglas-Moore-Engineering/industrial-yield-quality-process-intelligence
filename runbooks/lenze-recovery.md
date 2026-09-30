# Lenze artifact recovery and assurance

## Verified drill

`python -m iyqpis.lenze_recovery SOURCE FREEZE_SHA256 DECISION_SHA256 OUTPUT` operates only on temporary copies. The source release must match the independently recorded freeze and per-record decision hashes. The drill removes and corrupts each of four artifacts in turn, requires refusal, restores from the untouched release, and verifies identical decisions. It checks the original artifact hashes again after completion.

Eight cases passed on 2026-09-28; see [evidence](../.azure/lenze-recovery-evidence.json). Measured durations are local copy-and-score timings, not an approved RTO or a measurement of Azure disaster recovery. There is only one accepted Lenze release: this tests restoration of that release, not switching a running service between model versions.

## Azure recovery gap

Read-only inspection on 2026-09-28 found blob soft delete disabled, no container-delete retention policy, and no reported versioning or restore policy on the existing lake. Successful model uploads with checksum readback do not prove recoverability after deletion. Do not call this cloud backup/restore complete.

Before production promotion, select retention and recovery requirements with an accountable owner, validate service compatibility for the existing hierarchical-namespace account, preview the required infrastructure change, and exercise restore on isolated test objects. Never delete the actual accepted model to demonstrate recovery. Keep recoverable release copies and their independent integrity anchors until a verified policy supersedes them.

## Failure response

- Missing or altered artifacts: refuse scoring; recover the exact approved release from a trusted copy and recheck hashes and decisions.
- Invalid inputs: reject the batch; preserve diagnostics and correct source data rather than modifying acceptance thresholds.
- Private storage or identity failure: fail the execution; retain private access and diagnose DNS/RBAC. Do not enable a public storage endpoint as a workaround.
- Unexpected decisions: stop promotion and investigate runtime/artifact differences. Do not recalibrate using the inspected test set.

Existing platform Activity Log alerts are management-plane monitoring. Their existence does not prove that failed inference jobs generate notifications. Application failure alert coverage and delivery require separate implementation/verification; no alert message was sent by this drill.

Prepared follow-up: [reference operational assurance](reference-operational-assurance.md) includes an isolated whole-container cloud restore tool with checksum verification, context/retention guards and checkpointed evidence. Its simulated tests do not close the cloud-recovery gap above.
