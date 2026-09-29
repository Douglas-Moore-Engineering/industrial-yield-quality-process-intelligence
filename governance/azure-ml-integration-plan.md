# Azure ML integration plan

Status: workspace foundation deployed in East US 2; operator access, runtime permissions, registry/model integration and compute remain pending. Scope is the reference environment, not a customer production release.

## Confirmed design constraints

- Reuse the approved East US 2 resource group, VNet, compatible DNS zones, monitoring resources and registry where supported. Preserve existing workloads and network restrictions.
- The existing lake has hierarchical namespace enabled. Azure ML does not support it as default workspace storage, so add separate non-HNS default storage; retain the lake as a governed data source.
- Use identity-based system datastores with shared-key authorization disabled. Do not enable the registry admin account to satisfy an older creation example; use supported managed-identity association and verify it.
- Workspace inbound access stays private. Include workspace and default-storage private endpoints and DNS associations. A private workspace also requires a usable private client path for the operator.
- No automatic training schedule or always-on endpoint. Compute selection remains subject to quota, private connectivity and a zero-idle-node configuration.
- Preserve frozen Lenze model bytes, feature order and cutoff. Register existing evidence rather than treating repeat evaluation as new acceptance data.

## Private access finding

Windows per-user/all-user VPN checks returned no configured connections. The platform resource group contains no VPN gateway and the inventory contains no Bastion resource. This does not rule out external company-managed connectivity. The user asked us to check, and selection of a new access path is pending.

Azure retail API checked 2026-09-28: East US 2 VpnGw1 base rate USD 0.19/hour and VpnGw1AZ USD 0.21/hour (approximately USD 138.70/153.30 per 730 hours). Public IP, DNS/private resolver, transfer, private endpoints and other resources are additional. This is a public retail estimate, not a quote or spending cap. Gateway cost alone exceeds the existing 100-unit monthly platform budget; do not provision it without a reviewed cost decision.

Compare managed VPN (direct laptop access, ongoing gateway/DNS costs) with a private on-demand workstation (desktop/connection tooling, VM quota, disks, licensing and access-service costs must be verified). Do not introduce a public RDP/SSH endpoint or relax service networking to avoid designing private access.

## Remaining implementation and acceptance

1. Finalize operator private access and cost constraints.
2. Produce workspace/default-storage/identity/private-endpoint IaC and preview additive changes; confirm dependency permissions and service-provider readiness.
3. Provision and verify private DNS/TLS, Studio sign-in, identity access and default datastore behavior.
4. Register frozen model, environment and data references; configure and execute one bounded Azure ML job with idle compute at zero.
5. Finish the already prepared monitoring/retention deployment, private log queries, fault-alert delivery and isolated restore tests.
6. Walk the user through [the portal operating guide](../runbooks/azure-portal-guide.md), and record evidence for each action before claiming completion.

## Sources

- [Workspace default storage limitations](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-workspace?tabs=python)
- [Identity-based workspace storage](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-disable-local-auth-storage?view=azureml-api-2)
- [Managed identity service authentication](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-identity-based-service-authentication?view=azureml-api-2)
- [Private workspace access](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-configure-private-link?view=azureml-api-2)
