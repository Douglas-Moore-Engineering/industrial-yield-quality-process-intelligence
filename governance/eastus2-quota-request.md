# East US 2 learning quota requests

Requested 2026-09-28 through Azure CLI, after confirming the approved local account context. No compute was deployed.

| Provider | Family | Requested total | Last observed result |
|---|---|---:|---|
| Microsoft.Compute | standardDDSv5Family | 2 vCPUs | Failed: QuotaNotAvailableForResource; current limit remains 0 |
| Microsoft.MachineLearningServices | standardDDSv5Family, dedicated | 2 vCPUs | Failed: QuotaNotAvailableForResource; current limit remains 0 |

Submission success is not quota approval. Request identifiers and full responses are retained only in ignored `infra/azure/quota-*.local.json` files. Both requests have completed unsuccessfully; additional capacity requires review.

## Prepared Microsoft quota-review description

Please review availability of 2 dedicated Azure Machine Learning DDSv5-family vCPUs in East US 2 for one Standard_D2ds_v5 node. The automated quota request returned QuotaNotAvailableForResource. This is a temporary reference manufacturing model-validation walkthrough using an existing frozen CPU model. Proposed cluster bounds are minimum 0, maximum 1 node, on-demand jobs only, with a bounded job timeout and idle scale-down. No GPU, continuous endpoint, production customer data or recurring training schedule is requested. East US 2 is required. Please confirm whether this family can be enabled or identify an available two-vCPU CPU family in that region.

This description is prepared, not submitted as a support message. Use the approved company subscription in Azure's quota/support process; do not paste credentials. Quota allocation does not itself deploy resources or guarantee capacity.

Reference: [Azure ML quota management](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-quotas?view=azureml-api-2).
