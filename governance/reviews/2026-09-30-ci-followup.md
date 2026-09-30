# CI follow-up — 2026-09-30

This record follows [CR-DOC-REF-2026-09-30](2026-09-30-reference-review.md). It records fresh GitHub Actions results and a focused deployment-script correction. It does not represent an Azure deployment, independent assurance approval or customer acceptance.

## Evidence and correction

Documentation commit `8c3fa43604d654c4dcc3d514b8cdf4dbfd47e196` triggered the existing validation workflows:

- [Data validation run 36749210367](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/actions/runs/36749210367) passed: **90 tests passed**.
- [Platform validation run 36749210505](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/actions/runs/36749210505) failed in the deployment-guard tests. A valid `2026-09-01T00:00:00Z` budget start was rejected before the intended guard could be checked.

`ConvertFrom-Json` can return an ISO timestamp as a `DateTime`. The existing regex check converted that object to a culture-dependent string. Commit `740c6a4e724063e6607929185848647cd728399e` changes [platform.ps1](../../infra/azure/platform.ps1) to validate UTC, day one and midnight directly for parsed dates, and use exact invariant parsing for canonical string values. See Microsoft's [ConvertFrom-Json documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/convertfrom-json?view=powershell-7.5).

[Regression tests](../../infra/azure/Test-PlatformGuards.ps1) cover malformed/calendar-invalid values, wrong day/time, missing/noncanonical timezone, numeric/null values, valid previews under `en-US` and `fr-FR`, and refusal to deploy without explicit approval. Azure CLI calls are mocked. Account, tenant, subscription, environment and deployment-approval restrictions remain in place.

## Follow-up validation

[Platform validation run 36749939533](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/actions/runs/36749939533), at the fix commit, completed with these results:

| Check | Observed result |
|---|---|
| Six existing CI Bicep compile targets | Passed |
| Five PowerShell deployment/publishing/runtime guard scripts | Passed, including the new UTC-date and culture regressions |
| Simulated private-probe Python tests | 4 passed |
| Checkov 3.3.20 Bicep scan | 50 passed, 4 failed, 3 existing skips |
| Overall platform workflow | **Failed at the security scan** |

The date-validation defect is resolved. The remaining four scanner findings are in the pre-existing [Azure ML workspace template](../../infra/ml-workspace.bicep), which this correction does not change:

| Checkov finding | Observed template configuration | Required disposition |
|---|---|---|
| CKV_AZURE_36: trusted Microsoft services access | Storage uses `bypass: 'None'`, `defaultAction: 'Deny'`, and disabled public access | Review intended private/identity access against the scanner rule; do not broaden access merely to pass a check |
| CKV_AZURE_206: storage replication | `Standard_LRS` in the temporary reference workspace | Review recovery requirements and cost; record the chosen replication policy or an explicitly accepted reference-scope exception |
| CKV_AZURE_43: storage naming | Name is generated with `stml` plus `uniqueString(resourceGroup().id)` | Verify the evaluated name against service rules and determine whether the scanner can resolve the expression |
| CKV_AZURE_243: workspace private endpoint | `workspaceEndpoint` module targets `workspace.id` with group `amlworkspace`; public access is disabled | Verify module resolution and retained deployment evidence, then disposition the scanner finding; private-client acceptance remains pending |

These are unresolved scanner findings, not proof that every reported issue is a deployed vulnerability. No new scanner exclusions, relaxed access settings, replication change or cloud operation was introduced. RA-11 in the [assurance action register](../reference-assurance-actions.csv) tracks review and evidence needed to close the failed scan.

## Remaining limits

The Python/model implementation, thresholds, frozen artifacts and original requirement statements are unchanged by the script fix. The passing data result applies to `8c3fa43`; that suite is not claimed to have rerun at the PowerShell-only fix commit. The structural JSON report linked from the original review describes the earlier documentation-only correction and remains unchanged.

CI compilation and mocked guard tests do not prove deployed Azure behavior. Monitoring deployment, notification delivery, cloud restore, formal review/ownership and site acceptance remain open in the [assurance action register](../reference-assurance-actions.csv).

Subsequent evidence-supported scanner dispositions and executable security/operational checks are recorded in the [security and operations implementation review](2026-09-30-security-operations.md). That later platform CI run passes with explicit resource-scoped skips; the failed run and open cloud-operation limits above remain historical evidence.
