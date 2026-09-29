# Azure platform engineering

**Deployed** to East US 2 as the development platform foundation. Resource group: `rg-iyqpis-dev-platform`; subscription deployment: `iyqpis-dev-platform`. Azure reports Succeeded and all five private endpoint connections are Approved (vault, registry, Monitor, and the data lake's blob and dfs endpoints). Private-client data-plane acceptance for the original three endpoints remains pending. This development foundation follows the repository's [deployment topology](../../docs/diagrams/12_deployment_topology.mmd) and [OT boundary](../../docs/diagrams/05_ot_it_security.mmd). Original architecture baselines remain unchanged. Applications, industrial pipelines, ML workloads and plant connectivity are outside this implementation.

## Target

Target account, subscription and tenant belong in ignored `context.local.json`, never in shared files. The script checks all three before cloud operations and refuses missing or incomplete configuration. Local compilation requires no account configuration.

## Implemented foundation

| Capability | Resources and controls |
|---|---|
| Environment boundary | One tagged resource group per environment, subscription-scope Bicep |
| Network | Isolated VNet, /24 endpoint and reserved runner subnets, NSGs, no default outbound access |
| Private access | Vault, registry, Monitor and data lake (blob + dfs) endpoints; eight linked private DNS zones |
| Secrets | RBAC Key Vault, public access disabled, 90-day soft delete and purge protection |
| Artifacts | Premium ACR for Private Link, admin/anonymous/public access disabled, untagged-manifest retention |
| Data lake | ADLS Gen2 (HNS), `Standard_ZRS`, OAuth-only, public access disabled; `raw`/`validated`/`contextualized`/`curated-evidence` containers per the [data zones](../../docs/04-data-architecture-and-digital-thread.md#data-zones); separate from any future ML default storage |
| Identity | Publisher and runtime managed identities; registry-scoped AcrPush/AcrPull and data-lake-scoped Storage Blob Data Contributor/Reader |
| Monitoring | Log Analytics, workspace-based Application Insights, private-only AMPLS, vault/registry diagnostics |
| Delivery | Compilation, Checkov CI, account guard, ARM validation, what-if, explicit deployment switch |

The reserved runner subnet can access endpoints on HTTPS and Azure DNS on port 53; all other egress is denied. Endpoint ingress is allowed only from that subnet on HTTPS. No compute, runner, peering, gateway, public IP or plant route is created. A future runner requires approved egress for Entra, ARM, source control and package feeds before it can operate. Identities are not attached to workloads and have no federated trust yet. Neither identity receives vault secret access.

Private data-plane access requires a network-connected client. An ordinary laptop or hosted CI runner cannot query the private services. The CI workflow performs compilation/scanning only and needs no Azure credentials. ARM deployment operates through the control plane.

## Validate and preview

Prerequisites: Azure CLI, Bicep 0.47.16, Checkov 3.3.20 and PowerShell. Example region, CIDRs and retention are development assumptions, not approved production settings.

```powershell
./infra/azure/platform.ps1 -Action Validate
checkov -d infra/ --framework bicep --compact
Copy-Item infra/azure/dev.parameters.example.json infra/azure/dev.parameters.local.json
Copy-Item infra/azure/context.example.json infra/azure/context.local.json
```

Set your approved account email, subscription ID and tenant ID in the ignored context copy. Do not commit that file. Edit the parameter copy to set an approved location, cost center, owner, non-overlapping CIDRs and retention. Check [governance gates](../../governance/pre_azure_gate_status.md), regional availability, inherited policies, provider registration, budget and deployment permissions. The deployer needs subscription resource creation and role assignment permissions. No broad role is granted to workload identities.

```powershell
./infra/azure/platform.ps1 -Action Preview -ParametersFile infra/azure/dev.parameters.local.json
```

Review every what-if change. A first deployment should only add resources. Investigate modifications/deletions before approval. Premium ACR, endpoints, DNS and logs incur costs; tags are not a spending cap. After explicit approval of the preview and costs:

```powershell
./infra/azure/platform.ps1 -Action Deploy -ParametersFile infra/azure/dev.parameters.local.json -ApproveDeployment
```

The script revalidates/previews before deploying, uses incremental ARM behavior, and refuses production. It does not automatically classify the preview as safe. Reuse a deployment name only with the same deployment metadata location.

## Operational acceptance and remaining work

See [operations completion and runbooks](OPERATIONS.md) for the deployed budget, operational alerts and Activity Log export, plus CI activation, private acceptance and recovery procedures. Alert email delivery is verified. Private-client acceptance and protected GitHub deployment remain incomplete; see [release evidence](OPERATIONS-VALIDATION.md).

After deployment, record the template commit and deployment ID. From an approved private client, verify private DNS and Approved endpoint connections; confirm public access is denied; test publisher push/runtime pull and denied runtime push; generate audit events and verify log arrival; inspect effective routes/NSGs before attaching any workloads or connectivity.

Defender plans, policy assignments, locks, central hub integration, private runners and recovery infrastructure require organization-specific decisions and remain follow-up platform work. A monthly budget of 100 billing-currency units is deployed; it does not shut services down or cap spending. CI federation remains disabled because the current GitHub plan lacks required protections. No company-wide policies or management groups are changed. Production RPO/RTO, restore drills, classification/retention and acceptance gates remain pending.

For deployment failure, inspect ARM operations, fix the failed resource and redeploy. Do not delete the resource group to retry. Purge protection prevents early vault purging; preserve the vault name and follow recovery procedures. Reverting code does not reverse retained data or resource state.

## Design basis

Security scan exception: `CKV_AZURE_166` (registry quarantine) is explicitly deferred. There is no image scanner, release identity or promotion workflow, and blindly enabling quarantine would prevent normal image consumption. Revisit before onboarding images. No other checks are suppressed. Checkov results do not prove Defender scanning or zone redundancy is configured; those require explicit service/runtime verification.

- Bicep avoids a separate state backend; Terraform remains a multi-cloud alternative.
- Premium is required for the selected registry networking: [ACR Private Link](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-private-link).
- Monitor requires AMPLS associations and private DNS; the /24 provides room for its endpoint IPs: [Monitor configuration](https://learn.microsoft.com/en-us/azure/azure-monitor/fundamentals/private-link-configure).
- Stable hashed names follow [Azure naming limits](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules).
- No workload compute, ingestion, database or ML service is selected. Future ML default storage must be separate from an HNS-enabled lake: [ML dependencies](https://learn.microsoft.com/en-us/azure/machine-learning/concept-workspace?view=azureml-api-2).
- An isolated foundation preserves the OT boundary; it is not a complete enterprise landing zone or disaster recovery solution.

## On-demand data engineering

The existing lake is reused by the [batch implementation and release runbook](../../runbooks/data-engineering.md). The manual Azure job and isolated network additions are deployed in East US 2. Live Azure acceptance passed for all five sample datasets: 1,104,500 validated records, 16 artifacts, matching remote checksums, and replay without changing existing blobs. Registry and lake access remain private. No schedule is configured; job compute ends after execution. Existing storage, registry, networking and logging charges continue. Production source integration and the platform follow-ups above remain separate work.

## Reference AI validation

The [reference AI build sequence](../../runbooks/reference-ai.md) reuses the existing manual job through an execution-only immutable image override. Its first Azure run completed: verified feature preparation, chronological training/calibration/test, shadow safety checks, reference review evidence and five checksum-verified model/evidence artifacts. Replay succeeded with the same model ID and matching existing artifacts. The default data job image and schedule remain unchanged.

This is a reference industrial manufacturing environment with no approved customer plant or pilot owner. Copper rod/wire is illustrative.

Current model-validation state:
- **Lenze geared-motor quality-inspection reference benchmark: G2 PASS** — 65% anomaly recall and 7.74% false-alert rate on the publisher test partition, reproduced in Azure with frozen/checksum-verified evidence.
- **SECOM reference track: not accepted for promotion** — the earlier deployed baseline failed its alert-recall criterion and later candidate work still lacks independent confirmation.

Customer production promotion remains blocked because site-specific data, plant acceptance thresholds, operational assurance and release authority are absent. No live production inference service, OT control connection, production review application or validated digital twin is deployed. Use `Invoke-ReferenceAI.ps1 -ApproveRun` for approved on-demand reference validation; outputs are retained in the private curated-evidence container.
