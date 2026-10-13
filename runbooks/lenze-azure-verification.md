# Frozen Lenze verification in Azure

Completed 2026-09-28: execution `job-iyqpis-dev-data-rptcrd5` succeeded. Frozen-model evaluation reproduced 208/320 detected anomalies and 122/1,576 false alerts. The worker uploaded four artifacts with SHA256 readback. Registry public access is disabled with zero IP rules; the original data image and manual trigger are unchanged. Image digest: `sha256:75234c6d1fe17485fb36d8d1a0918eec89bf8f6a4ee54c4c285129eb3056fe51`.

This reference workload reuses the existing manual Container Apps job in East US 2. It does not provision infrastructure or use azd. Existing account, private-registry and compute guards remain in the execution scripts.

## Validation and execution

1. Preserve `artifacts/lenze/v1` from the frozen local benchmark. Keep its model SHA256, source checksums, feature order and cutoff unchanged.
2. Stage only the two public CSV files, frozen model, freeze/evaluation JSON and Lenze Python modules in an isolated container build directory. Do not include credentials or local Azure parameter files.
3. Build on the existing pinned ML image. Run locally and require matching test counts before publishing.
4. Publish with `Publish-DataImage.ps1`, using separate ignored `lenze-job.parameters.local.json`. The existing approval covers a temporary single IPv4 registry rule; the script restores disabled public access and zero rules in `finally`.
5. Run `Invoke-LenzeVerification.ps1 -ApproveRun`. It checks account context, manual trigger, inactive executions, immutable image, private registry and the existing 2 CPU/4 GiB compute bounds. It overrides only this execution.
6. Verify execution success and evidence publication. `azure_lenze.py` checks frozen source/model hashes before loading the trusted model, recomputes test metrics, and fails on mismatched counts. It uses managed identity and private DNS, then uploads model and evidence with no overwrite and checksum readback.

Evidence prefix: `curated-evidence/lenze/<model-sha256>/`. The final `azure-verification.json` is uploaded after model, freeze and local evaluation. Consumers should require all four files. The report field `exact_decisions_match` currently checks aggregate TP/FP counts, not individual prediction identities; interpret it only as matching evaluation counts.

The workload is a reference benchmark, not an always-on inference endpoint or customer production release. There is no retraining or threshold adjustment in cloud verification. Original data-job configuration and manual scheduling remain in place.

## Individual decision consistency

`Invoke-LenzeVerification.ps1 -ApproveRun -VerifyDecisions` runs the reviewed `lenze_verification.py` through an execution-only command override in the same immutable image. It checks an externally supplied frozen-manifest hash, source/model payload hashes, identifier uniqueness, complete joins, partition values and finite features before model scoring. The manifest hash is an integrity anchor from the local release artifact, not a cryptographic signature.

The verifier hashes sorted `(record identifier, alert decision)` pairs. Reordering rows preserves the digest; swapping which records alert changes it even if totals remain identical. This verifies binary decisions, not bitwise equality of floating-point scores. Preserve the verifier code hash and execution name with the result. This check does not modify the existing private model evidence or reproduce upstream audio extraction.
