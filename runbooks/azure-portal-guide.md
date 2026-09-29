# Operating the IYQPIS reference environment in Azure

## Start here

Open https://portal.azure.com, select the approved company directory and subscription, then open **Resource groups > rg-iyqpis-dev-platform**. Use the resource group's Type filter to find each service. Account identifiers are intentionally excluded from this guide.

| Service | Current resource | What you do there |
|---|---|---|
| Azure Managed Grafana | `grafana-iyqpis-dev` | Private service deployed and connected to AMPLS; dashboard imported and read back; live queries still fail private-link validation |
| Azure Machine Learning | `mlw-iyqpis-dev` (foundation deployed) | Workspace exists; model registration, compute and private Studio access remain pending |
| Container Apps Job | `job-iyqpis-dev-data` | Open execution history to see current batch runs, status and logs; this is where verified reference jobs currently run |
| Container Apps environment | `cae-iyqpis-dev-data` | Network and log destination configuration for the job |
| Log Analytics | `log-iyqpis-dev` | Query retained platform and job telemetry from an authorized private-network client |
| Application Insights | `appi-iyqpis-dev` | Application telemetry resource; resource existence alone does not mean every worker is instrumented |
| Storage account | `st4ilak3xb4dmrk` | Containers: raw, validated, contextualized, curated-evidence; data access requires private connectivity and data-plane permission |
| Container Registry | `cr4ilak3xb4dmrk` | Immutable container images used by jobs; not the ML model registry |
| Key Vault | `kv-4ilak3xb4dmrk` | Platform secrets/key management boundary; do not copy secrets into documentation |
| Virtual network | `vnet-iyqpis-dev` | Private endpoints, DNS connectivity and job subnet |
| Monitor alerts | Existing platform alerts | Health, failed management operations and access changes; proposed job/model alerts are not deployed yet |
| Workbooks | Proposed IYQPIS Reference Operations | Monitoring dashboard prepared but not deployed or validated yet |

Azure resource blades can be visible even when private data access is unavailable. Seeing the storage resource is not the same as being able to read blobs; seeing a workspace does not establish Studio connectivity. A normal internet-connected Cloud Shell is not automatically inside this VNet.

## East US 2 learning-compute prerequisite

The regional preflight found `Standard_D2ds_v5` listed without a location restriction and supported by Azure ML, but both DDSv5 family quotas are zero. In **Subscriptions > your approved subscription > Usage + quotas**, filter to **East US 2** and review these separate limits:

| Provider | Family | Required total limit for the proposed walkthrough |
|---|---|---:|
| Microsoft.Compute | Standard DDSv5 Family | 2 vCPUs for one temporary workstation |
| Microsoft.MachineLearningServices | Standard DDSv5 Family, dedicated cores | 2 vCPUs for one on-demand ML node |

Requesting quota does not create compute or guarantee allocation. Both quota requests have now been submitted. Compute is processing; Azure ML failed with QuotaNotAvailableForResource. See [request status and review draft](../governance/eastus2-quota-request.md); do not duplicate the pending request. See [Microsoft's quota instructions](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-quotas?view=azureml-api-2). Workspace provisioning itself does not require allocating these VM cores; the quota is needed for the proposed usable walkthrough. The workspace, access path, permissions, model registration and job still need implementation and validation.

## Inspect an existing execution

1. Select `job-iyqpis-dev-data`, then execution history.
2. Inspect the desired execution and its logs. A Succeeded status confirms execution, not necessarily a passing model criterion; inspect the evidence too.
3. The default job runs the data pipeline. Use the reviewed repository launch scripts for Lenze verification because they supply an execution-specific image and command. Do not use a bare portal Start expecting it to run the Lenze model.
4. The accepted Lenze evidence is under `curated-evidence/lenze/<model-sha256>/`. Resolve the exact hash from `.azure/lenze-acceptance.json`.
5. The manual job has no daily schedule. Check that executions are finished after use. Private endpoints, registry, retained data and logs can still incur charges while compute is idle.

## Planned ML Studio workflow

After workspace provisioning and private access have been verified, open the workspace resource and **Launch studio**, or open https://ml.azure.com and select the workspace. The intended workflow is **Data > Environments > Jobs > Models**: version the source, register the frozen runtime, run an on-demand verification job, inspect metrics/artifacts and register the accepted model with its evidence. These assets do not exist merely because the workspace exists; each must be registered and tested.

ML job compute should use a zero-node idle setting when supported and verified. Interactive compute instances require explicit start/stop or idle shutdown controls. Do not start a notebook VM or deploy an online endpoint merely to browse model metadata. A future endpoint would have its own cost and release review.

## Completion walkthrough

The environment is not complete until the user can connect privately, open Studio, locate the frozen model, run one bounded job, inspect its evidence, open the monitoring workbook, verify an alert, recover a disposable test object and identify idle costs. These are acceptance checks, not claims of work already completed.
