# Azure batch-inference deployment results

The frozen Lenze-QI reference model ran successfully in Azure East US 2 on 2026-09-29 UTC (2026-09-28 US Eastern). Execution `job-iyqpis-dev-data-yrcuuy2` used the existing private, manually triggered Container Apps job. **Deployment status: verified for the reference batch-inference system.** The deployed runtime is Azure Container Apps Jobs.

## Verified replay

| Check | Result |
|---|---|
| Azure execution | Succeeded |
| Publisher test records | 1,576 |
| Alerts | 330 |
| Decision consistency | All record-level decisions match the previously verified digest |
| Frozen model, source and freeze integrity | Checked before inference |
| Local software tests | 90 passed |
| Run schedule | Manual, on demand |

[Machine-readable execution evidence](../.azure/github-validation-result.json) records the model, freeze and decision hashes. The full Azure response and raw logs remain in ignored local files.

## Reference benchmark results

The prior labeled evaluation used this same frozen model and publisher partition. The new replay confirms the same decisions; it is not a new independent test set.

| Metric | Result | Fixed criterion |
|---|---:|---:|
| Detected anomalies | 208 of 320 | — |
| Recall | 65.00% | At least 50% |
| False alerts / all records | 122 / 1,576 = 7.74% | At most 10% |
| ROC AUC, prior labeled evaluation | 0.885554 | Not an acceptance gate |

The 7.74% measure uses **all records** as its denominator; it is not the conventional false-positive rate among normal records. The reference point-estimate criteria pass. Frozen cutoff: `0.47010843494548926`. See [labeled evaluation evidence](../.azure/lenze-acceptance.json) and [reference protocol](../governance/lenze-protocol.json).

## Deployed scope

Private storage, container registry, managed identities, networking and on-demand model inference are deployed in Azure. The successful execution above verifies the frozen model on the publisher reference dataset. Prior cloud artifact upload/readback evidence is separate from this decision replay.

Grafana, Azure ML-managed execution and desktop access are optional follow-on integrations, outside this batch-deployment acceptance scope. Their detailed status is retained in [project status](../PROJECT_STATUS.md). They are not prerequisites for the successful Container Apps execution reported here.

This is a reference validation deployment using publisher precomputed features. Customer production acceptance, independently reproduced feature extraction and field-performance validation are outside this result. No continuously running model endpoint was created; retained Azure services still incur charges.

## Reproduce

Use the approved company context in ignored local Azure parameters and the published immutable Lenze image. From the repository root:

```powershell
./infra/azure/Invoke-LenzeVerification.ps1 -ApproveRun -VerifyDecisions
```

The command incurs bounded job charges and returns a submission, not a completion verdict. Inspect execution status and compare its printed decision digest with the evidence file. Preserve frozen inputs and thresholds; do not label repeated evaluation of these records as fresh acceptance data.

This results page and its evidence contain no account email, subscription ID, tenant ID, access token or credentials. They are published as repository evidence. Publication does not imply a new Azure execution or production release.
