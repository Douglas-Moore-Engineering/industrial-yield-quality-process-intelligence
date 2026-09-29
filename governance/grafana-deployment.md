# Grafana deployment review

Status: deployment `grafana-learning` succeeded. Grafana public access/API keys are disabled; its managed AMPLS connection is Approved after approval and synchronization, and inbound endpoint DNS association succeeded. Dashboard import and readback through the existing private job succeeded. The Grafana-to-Log-Analytics query failed with PrivateLinkValidationFailedError; monitoring is not yet operational. Explicit api.loganalytics.io routing was applied and synchronized but did not resolve the failure. Region: East US 2 only. The user instructed deployment after the cost review.

`infra/grafana.bicep` compiles successfully. Azure what-if reports 8 creates, 62 ignored resources, no modifications or deletions. Nested endpoint resources are included through a module. Checkov is unavailable and was not run; compilation and preview do not establish security or runtime acceptance.

## Proposed connections

- Azure Managed Grafana Standard, system identity, public access and API keys disabled.
- Grafana managed private endpoint to existing AMPLS for Log Analytics queries; approval and synchronization required after creation.
- Monitoring Reader assigned only on the existing Log Analytics workspace.
- Grafana Admin assigned only on this Grafana resource to the approved signed-in operator; object ID is in ignored local parameters.
- Private inbound endpoint and DNS zone/VNet link. Usable operator connectivity remains unresolved; do not open public access as a shortcut.
- Dashboard import template: `infra/grafana/reference-operations.json`, with job events and structured model/data observations. Substitute the local workspace resource ID and managed-identity data source at import. Dashboard queries have not been executed. The model-monitoring image is not yet deployed, so missing model events are expected and must not display a healthy status.

## Cost and stop behavior

Azure Retail Prices API snapshot `artifacts/pricing/grafana.json` reports East US 2 Standard Node at USD 0.034246/hour (about USD 25 per 730 hours) and Standard User at USD 6/month per active user. Zone redundancy is disabled. The private inbound endpoint adds approximately USD 0.01/hour; DNS, data-source private-link usage, logs and traffic are additional. Existing services continue billing separately. Do not assume the monthly active-user charge is prorated for a two-hour walkthrough. Grafana has no configured shutdown/deletion automation; this template leaves it provisioned until explicitly removed. This is not a complete bill or hard spending cap.

Microsoft documents managed outbound private endpoints as free, with possible charges on the target data source. Standard is required for this connection. Sources: [private data sources](https://learn.microsoft.com/en-us/azure/managed-grafana/how-to-connect-to-data-source-privately), [pricing](https://azure.microsoft.com/en-us/pricing/details/managed-grafana/).

## Remaining deployment acceptance

Completed: user deployment instruction after cost review, incremental deployment, new connection approval and synchronization. Remaining: verify managed identity queries; import the dashboard through an authorized private client; verify real events and no-data behavior. Export dashboard evidence before deleting only the Grafana resources after the walkthrough. Do not delete the shared AMPLS, Log Analytics, VNet, ML workspace or other shared services.

Both DDSv5 Compute and Azure ML quota requests now report Failed with QuotaNotAvailableForResource. Grafana does not resolve model compute or private workstation availability. ML model deployment remains pending.

## Private configuration execution

`infra/grafana/configure.py` runs inside the existing bounded data job with temporary Grafana Admin permission removed afterward. It checks private DNS, uses managed identity, provisions the data source, imports and reads back the dashboard, then requires a successful query. Dashboard import passed; the query failed. No public access was enabled. Full-system completion must not be inferred from dashboard existence.
