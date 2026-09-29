# Temporary Azure ML walkthrough estimate

Prepared 2026-09-28 using the Azure public retail API; USD, East US 2 unless the meter is global. Pricing preceded deployment. The workspace foundation has now deployed: three new private endpoints add approximately $0.03/hour ($21.90 over 730 hours), plus DNS, storage and traffic charges. No compute was deployed. These retained services have no automatic shutdown.

## Allocation preflight update

### East US 2 constraint rechecked

The user requires East US 2 only. A full regional SKU, Compute quota, Azure ML size and Azure ML quota check found no eligible two- or four-vCPU combination with available quota. `Standard_D2ds_v5` is listed without a location restriction and is supported by AmlCompute, but both the Compute DDSv5 family quota and Azure ML dedicated DDSv5 family quota are zero. Regional totals alone do not resolve these family limits. A candidate learning configuration needs 2 Compute-family vCPUs for the workstation and 2 ML dedicated-family vCPUs for one job node; quota approval and actual allocation remain pending. No region migration is planned. Evidence: ignored `infra/azure/eastus2-readiness.local.json`.

### Alternative-region check, 2026-09-28

East US has an unrestricted `Standard_D2as_v4` listing with sufficient Compute quota. Azure ML independently lists this size for AmlCompute, with 10 dedicated family vCPUs and 20 dedicated regional vCPUs available (zero used). Allocation is still subject to capacity at deployment time. Standard on-demand retail rates are $0.096/hour Linux and $0.188/hour Windows, or $0.568 for two hours of both machines before all supporting services. Spot and low-priority prices are excluded.

This does **not** validate the earlier full walkthrough subtotal: Microsoft's current Bastion Developer region list includes Central US and East US 2, but excludes East US and West US 2. Central US's checked eligible two-vCPU sizes do not simultaneously have Azure ML support and sufficient ML family quota. A usable private operator-access design and its complete incremental price remain unresolved. No alternative-region resources were deployed; the existing East US 2 platform is unchanged.

Read-only evidence is saved in ignored `infra/azure/learning-eligible.local.json`, `infra/azure/learning-ml-quota.local.json`, and `artifacts/pricing/eastus-d2asv4.json`. These files may contain account identifiers and must remain private. Next preparation must resolve operator access before presenting a deployable cost and deployment preview.

Azure reports `Standard_D2s_v3` as `NotAvailableForSubscription` in East US 2. The rates below remain illustrative and are not a deployable quote for this subscription. Alternative VM allocation and their prices must be checked before proceeding. Azure ML provider registration is now complete. The workspace foundation template `infra/ml-workspace.bicep` compiles with the 2025-06-01 API, but is not deployed.

## Proposed learning scenario

Use a temporary private Windows workstation through Bastion Developer, browse ML Studio, register the existing model, and execute a single CPU batch inference/verification job. This does not propose a continuously running online endpoint. Two hours of workstation and ML-node time are assumed for illustration; actual provisioning and walkthrough time can differ. VM quota was previously observed for Dsv3, but Azure ML quota, regional allocation and Bastion deployment must still be validated.

| Component | Retail unit rate | Illustrative two-hour amount |
|---|---:|---:|
| Windows Standard_D2s_v3 workstation | $0.188/hour | $0.376 |
| Linux Standard_D2s_v3 ML node | $0.096/hour | $0.192 |
| Three additional private endpoints (workspace, blob, file), assumed topology | $0.01/endpoint-hour | $0.060 |
| One E10 LRS workstation disk | $9.60/month | approximately $0.026 using 730 hours/month |
| Bastion Developer | Free service tier | $0 |
| Standard NAT gateway | $0.045/hour + $0.045/GB processed | $0.090 before traffic |
| Standard static IPv4 for NAT | $0.005/hour | $0.010 |
| **Illustrative subtotal** | | **approximately $0.75 before traffic and other listed costs** |

This is not an all-inclusive quote: ML-node storage/load-balancer charges, additional endpoints if required, private DNS, storage capacity/operations, transfer and logs remain dependent on final topology and runtime. DNS/egress reachability from the private workstation and ML compute require validation; do not assume a new VM has usable default outbound connectivity. A $5 incremental planning allowance may be a useful target for a short session, but is neither a verified total nor an enforceable spending cap. Do not provision until the unresolved costs and final topology are reviewed.

Existing platform costs are excluded. The existing Premium registry, private endpoints, retained storage and logs continue billing independently of this walkthrough. Stopping a workstation stops VM compute charges only after deallocation; its disk still bills. Three new private endpoints left for 730 hours would add $21.90, plus other resources. A zero-node ML cluster avoids active-node compute charges but does not eliminate supporting-resource costs.

## End-of-session checks

Save evidence and the model registration identifiers; confirm all jobs ended; scale ML compute to zero or remove the temporary compute; deallocate the workstation; review temporary disks/endpoints/storage and explicitly remove only approved demonstration resources. Preserve existing platform resources unless the user separately authorizes their removal. No automatic deletion of shared services is implied.

## Sources

- Rate snapshots: ignored `artifacts/pricing/vm_dsv3.json`, `disk.json`, `network.json`, queried from https://prices.azure.com/api/retail/prices.
- [Bastion Developer pricing and regions](https://learn.microsoft.com/en-us/azure/bastion/bastion-sku-comparison)
- [Azure ML pricing](https://azure.microsoft.com/en-us/pricing/details/machine-learning/)
- [ML compute cost controls](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-optimize-cost?view=azureml-api-2)
