# Azure ML static-scan dispositions — 2026-09-30

## Scope and authority

The user requested evidence-supported security and operational corrections. This engineering record applies only to the existing temporary Azure ML workspace foundation: no ML compute, online/batch endpoints, customer data or production authority. It does not grant independent security approval, accept production recovery risk, or establish live Azure validation.

Four resource-scoped Checkov annotations in [the ML template](../infra/ml-workspace.bicep) are paired with a mandatory [compiled-template security check](../infra/azure/check_ml_security.py) and [negative regression tests](../infra/azure/test_ml_security.py). There is no global skip list or soft-fail setting. Both platform validation and the deployment validation job run these checks. All top-level Bicep entrypoints now compile in CI, including ML, monitoring, recovery and Grafana.

## Findings and disposition

| Finding | Pinned scanner behavior and repository evidence | Disposition and remaining limit |
|---|---|---|
| CKV_AZURE_36 | The Bicep check fails `defaultAction: Deny` with `bypass: None`. This workspace intentionally requires private access without a trusted-service network bypass. | Retain the stricter boundary. Compiled check requires disabled public/shared-key/anonymous access, HTTPS/TLS and no bypass. Actual identity/private-client access remains pending. |
| CKV_AZURE_43 | The inherited name check matches a literal against a naming regex; the template uses `stml` plus Bicep `uniqueString(resourceGroup().id)`. The function supplies a 13-character suffix, yielding a deterministic 17-character lowercase-alphanumeric name. | Expression-evaluation limitation. Pin the compiled expression and fail if it changes. The retained workspace deployment record also identifies the resulting storage name. |
| CKV_AZURE_243 | Despite its broad title, the pinned check looks for `managedNetwork.outboundRules` containing type `PrivateEndpoint`. It does not inspect the separately declared inbound private endpoint. This foundation has managed networking disabled and no ML compute. | Rule/design mismatch, not proof that inbound Private Link is absent. Verify workspace, blob and file endpoint modules, target IDs, service groups, DNS associations and private access in compiled configuration. Adding managed compute requires a new outbound-network design and review. |
| CKV_AZURE_206 | The check accepts only GRS/RAGRS/GZRS/RAGZRS; the existing temporary workspace uses LRS. Microsoft documents that geo-redundant default-storage failover is not Azure ML workspace failover. | **Reference-scoped policy deviation**, not a false positive or completed DR control. Preserve the current deployed design and cost profile. The compiled guard pins LRS and rejects ML compute/endpoint additions. Regional recovery, important artifact protection and production replication selection remain open. |

The LRS disposition authorizes this bounded source-validation scope; it is not an owner-signed production risk acceptance. The organization owner and security reviewer remain unassigned in the assurance register. Before the first Azure ML training job, irreplaceable artifact, customer data, managed compute, online endpoint, availability commitment or network expansion, reassess all four dispositions and establish a reviewed recovery/network baseline. Do not reuse these annotations for a customer deployment.

## Verification and limits

CI execution results are recorded in [the assurance implementation review](reviews/2026-09-30-security-operations.md). A green scan with documented skips is not equivalent to satisfying the skipped generic policies. The additional contract verifies the particular configuration being retained; it does not prove service authorization, DNS/TLS reachability, restore behavior or notification delivery in Azure. Existing unrelated scanner exceptions are unchanged.

Operational closure remains in [RA-03/04/06/09/11](reference-assurance-actions.csv). Historical failed scan results in the earlier CI follow-up remain preserved.

## Sources inspected

- Checkov **3.3.20**: [trusted-service rule](https://github.com/bridgecrewio/checkov/blob/3.3.20/checkov/bicep/checks/resource/azure/StorageAccountAzureServicesAccessEnabled.py), [name rule](https://github.com/bridgecrewio/checkov/blob/3.3.20/checkov/arm/checks/resource/StorageAccountName.py), [ML outbound rule](https://github.com/bridgecrewio/checkov/blob/3.3.20/checkov/arm/checks/resource/AzureMLWorkspacePrivateEndpoint.py), [replication rule](https://github.com/bridgecrewio/checkov/blob/3.3.20/checkov/arm/checks/resource/StorageAccountsUseReplication.py).
- Microsoft: [Bicep uniqueString](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/bicep-functions-string#uniquestring), [Azure ML disaster recovery](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-high-availability-machine-learning?view=azureml-api-2), [trusted-service storage access](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-trusted-azure-services).
- Existing project evidence: [workspace integration plan](azure-ml-integration-plan.md) and [original failed CI run](reviews/2026-09-30-ci-followup.md).
