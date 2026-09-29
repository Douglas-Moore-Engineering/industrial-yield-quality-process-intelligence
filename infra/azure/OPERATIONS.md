# Platform operations completion

This is the development platform operating procedure. It does not authorize production workloads, OT connectivity, model deployment or changes to enterprise-wide policy.

## Release state

The foundation and operations release are **deployed** (2026-09-28): a resource-group budget, one email action group, four Activity Log alerts, subscription Activity Log export to the existing workspace, and a dedicated deployment identity. Deployment `iyqpis-dev-operations` succeeded after an eight-create, zero-modification/deletion preview. Alert recipient and identifiers exist only in ignored local files.

Approved budget: 100 units of the subscription billing currency per month; actual alerts at 50%, 80%, 100%, forecast at 100%. The previous retail estimate used USD; confirm billing currency in Cost Management. A budget is neither a cap nor automatic shutdown. Cost Management currently returns no posted month-to-date rows for this resource group; that does not mean it is free.

Health alerts cover Service Health at subscription scope, platform Resource Health degradation/unavailability, failed management operations, and successful role assignment changes. Some PaaS resources do not emit Resource Health events. This is infrastructure monitoring, not an application availability SLO. Email delivery verified on 2026-09-28: after recipient verification and a new test, the user confirmed receipt of the Azure test email. Azure also reported test state Complete and receiver status Succeeded (CLI exit 0). See [action group email verification](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/action-groups).

Subscription Activity Log export includes other future resources in this subscription. It routes to the current private workspace, with its existing retention. No paid Defender plan, log-search alert, firewall, gateway, standing runner, or backup service is enabled by this release.

## Release commands

```powershell
./infra/azure/platform.ps1 -Action Validate -TemplateSet Operations
./infra/azure/platform.ps1 -Action Preview -TemplateSet Operations -ParametersFile infra/azure/operations.parameters.local.json
# After approving the actual preview, costs and alert recipient:
./infra/azure/platform.ps1 -Action Deploy -TemplateSet Operations -ParametersFile infra/azure/operations.parameters.local.json -ApproveDeployment
./infra/azure/Test-LivePlatform.ps1 -IncludeOperations
```

Keep budget start on the first of the chosen month and stable on redeploy. Do not copy example files over working local configuration. Deployment logs and ARM responses can include account identifiers: save them as `infra/azure/*.local.json`, never as committed evidence.

## Private acceptance probe

`Invoke-PrivateProbe.ps1` proposes a short-lived Linux VM on the existing runner subnet. It has no public IP, no added inbound rule, SSH passwords disabled, Trusted Launch, encryption at host and a managed boot log. Existing runner egress restrictions remain in place. It uses built-in Python and managed identities; it needs no public package downloads.

It verifies private DNS addresses inside the endpoint subnet, TLS/certificates, registry scoped tokens, real publisher push initiation/cancellation, denied runtime push, and denied runtime vault access. It does not create a workload image, read secrets, prove an actual image pull, or assert that audit events have reached Log Analytics. Those distinctions matter: a network/RBAC test is not a complete application acceptance test.

Preflight found `Standard_B2ls_v2` supports encryption at host in East US 2; its zone placements are restricted, so the template uses regional placement. The `EncryptionAtHost` subscription feature is Registered. The approved probe attempt failed preflight: `standardBsv2Family` quota is zero and two vCPUs are required. No probe resources remain. The request for two family vCPUs failed with QuotaNotAvailableForResource. Resolve availability through Azure quota/support before retrying. Public retail VM rate retrieved for Linux: USD 0.0416/hour, plus its temporary Standard SSD disk and diagnostics storage. This is a runtime estimate, not a spending cap or a guarantee of available capacity.

```powershell
# Only after approving temporary compute/disk charges and reviewing the template:
./infra/azure/Invoke-PrivateProbe.ps1 -ApproveTemporaryCompute
```

The runner polls for at most 15 minutes after deployment and deletes the uniquely named VM, NIC and OS disk in `finally`. An independent Azure shutdown schedule provides a one-hour fallback if the client disappears. Shutdown does not remove billable disks; if cleanup fails, inspect `private-probe-resources.local.json`, remove only those named resources, and verify they are gone. No cleanup deletes the platform resource group. The live data-plane checks have not run because allocation was blocked by quota.

## GitHub deployment activation

The repository contains validation and manual deployment workflows. Creating YAML alone does not configure GitHub. Activation was attempted: the current private-repository plan rejects required environment reviewers (HTTP 422) and branch protection (HTTP 403). The environment has no protection rules; therefore no Azure federation or deployment role is enabled. Use the guarded local operator deployment until supported protections are configured.

1. Protect `main` with pull-request review and required Platform validation checks. Restrict who can change `.github/workflows/` and `infra/`.
2. Create GitHub environment `platform-dev` with required reviewer(s), deployment allowed from **main only**, and no administrator bypass where supported. If repository licensing does not support the required protections, keep federation disabled and use operator deployments.
3. Set environment secrets `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, and `PLATFORM_PARAMETERS` (the approved dev parameter JSON). Set environment variable `PLATFORM_RESOURCE_GROUP`. Do not put any IDs in YAML. No client secret is used.
4. Verify the exact OIDC `sub` emitted for this repository/environment. Current GitHub subjects may include immutable owner/repository IDs or custom claim templates; do not guess the legacy format. Set only the verified subject in ignored operations parameters and preview the addition of federation/RBAC. Do not add a second branch credential that bypasses the environment.
5. Deploy the reviewed identity trust. Contributor is scoped to this resource group; it cannot grant roles or make subscription deployments. Bootstrap RBAC remains an operator task. Keep `githubSubject` empty until the environment protections have been checked. Empty settings do not revoke previously installed federation; removal needs an explicit reviewed change.
6. Run the manual workflow with `apply=false`; inspect the sanitized preview. Then run with `apply=true` and approve the protected environment. No PR job receives Azure tokens.

`foundation-ci.bicep` updates the existing foundation in incremental mode, preserving role assignments. The workflow refuses non-main/manual executions and destructive/unresolved previews. It does not prove a proposed modification is safe; inspect changes before approval. The deployment identity is powerful within this resource group: protect branch and environment access accordingly.

A hosted runner is sufficient for ARM control-plane deployment. Private registry publishing and private data-plane tests need a private client. No permanent self-hosted runner is installed in this development baseline, avoiding another idle expense. Add one only when image publishing workloads exist and approved egress is designed.

## Incident and recovery procedures

| Signal | Operator response |
|---|---|
| Budget threshold/forecast | Inspect Cost Analysis by resource and meter; check orphan probes; pause new deployments. Do not delete data-bearing services automatically. |
| Failed ARM operation | Read deployment operations; fix and redeploy incrementally. Preserve existing resources. |
| Service/Resource Health | Confirm Microsoft incident and affected service; record duration; rerun acceptance after recovery. |
| Unexpected role change | Identify caller in Activity Log; revoke unintended assignment/trust; inspect GitHub runs; preserve logs. |
| Private DNS failure | Inspect zone groups, VNet links and effective NSGs; do not enable public access as a workaround. |
| CI login failure | Compare exact issuer/subject/audience, environment protection, secret settings and RBAC propagation. Never add wildcard trust. |

Recover infrastructure from the reviewed Bicep revision. A template rollback does not restore deleted data. Key Vault soft-delete recovery is available within its configured 90 days; purge protection prevents early purge. No secrets or application data have been onboarded, so no backup/restore claim is made. Before storing irreplaceable images, define an export/replication policy and test recovery. Log Analytics retains the configured window; it is not an immutable compliance archive.

Production is explicitly incomplete until owners approve availability, RPO/RTO, data retention, backup/restore tests, compliance policies and support responsibilities. Central hubs, management groups and company-wide policies are separate enterprise integration work, not silently included in this isolated development subscription.

## Sources

- [Azure budget behavior](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets)
- [Activity Log export](https://learn.microsoft.com/en-us/azure/azure-monitor/platform/resource-manager-diagnostic-settings)
- [Activity Log alerts](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-create-activity-log-alert-rule)
- [GitHub OIDC claims](https://docs.github.com/en/actions/reference/security/oidc)
- [GitHub OIDC with Azure](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure)
