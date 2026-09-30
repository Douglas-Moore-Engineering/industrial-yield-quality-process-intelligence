# Reference monitoring and cloud recovery verification

## Contents

- [Prerequisites and limits](#prerequisites-and-limits)
- [Monitoring observation and notification receipt](#monitoring-observation-and-notification-receipt)
- [Disposable cloud recovery](#disposable-cloud-recovery)
- [Evidence and cleanup](#evidence-and-cleanup)

## Prerequisites and limits

[reference_assurance.py](../infra/azure/reference_assurance.py) is prepared and safety-tested with simulated clients. **No live execution is established by its presence or unit tests.** Use an authenticated private client with Azure CLI, the expected ignored `infra/azure/context.local.json`, and dependencies from `requirements-data.txt`. No new role or public-network access is granted by this tool.

The existing [monitoring/retention completion plan](../governance/monitoring-completion-plan.md) remains the deployment prerequisite. Preview any infrastructure change, confirm intended scope/cost and preserve existing resources. The CLI refuses recovery unless container soft delete is already enabled for 7–30 days. It does not enable it automatically.

This workflow is limited to `rg-iyqpis-dev-platform` in the expected account context. It does not establish production RPO/RTO, regional disaster recovery, Azure ML workspace failover, model-version rollback or site acceptance.

## Monitoring observation and notification receipt

1. Verify the prepared monitoring deployment and the existing private workspace/action group. Do not change recipients or open public log-query access for the test.
2. Generate a unique run identifier: in PowerShell, `$runId = [guid]::NewGuid().ToString('N')`.
3. Schedule one explicitly approved manual diagnostic execution using an execution-specific override of the existing job and a reviewed immutable image. Preserve the default job template, image, schedule, identity and bounds. The diagnostic command must emit the JSON produced by `python infra/azure/reference_assurance.py emit-diagnostic --run-id $runId` into **the job's console** and exit with code 1. Running this command on a laptop only prints a local fixture and is not Azure evidence. The script is repository tooling; ensure its code is supplied to the diagnostic job rather than assuming it is in the existing image. Never damage the accepted model or input to induce failure.
4. From the private client, query only that diagnostic run after logs arrive:

```powershell
python infra/azure/reference_assurance.py inspect --run-id $runId --output "artifacts/assurance/$runId/monitoring.json"
```

The read-only check records whether the two rules are enabled, scoped to the expected workspace and routed to the existing enabled action group with receivers. It counts matching diagnostic failure events over two hours. Missing events or routing yield `pending`; query/authorization errors yield `failed`. Use a new output filename for a later observation because existing evidence cannot be overwritten.

5. Separately record the alert instance/evaluation time and the actual notification receipt through the intended channel, linked to the rule, job execution, run identifier and time window. A receiver entry, successful log query, rule existence or action-group test alone does not prove the complete detection path. The tool always leaves `notification_delivery_verified` and `end_to_end_verified` false; a reviewer must reconcile real receipt evidence. No recipient message is sent by this script.
6. Confirm the diagnostic execution is terminal and the default job configuration remains unchanged. Diagnostic events carry `diagnostic: true` and `scope: reference_diagnostic`; exclude them from model/business acceptance metrics.

## Disposable cloud recovery

Use the approved reference lake account. This drill restores a **whole disposable container and its one probe blob**, which supports the existing hierarchical-namespace lake. It does not exercise individual-blob undelete, source-model deletion or regional failover.

```powershell
$runId = [guid]::NewGuid().ToString('N')
$storageAccount = 'REPLACE_WITH_APPROVED_REFERENCE_ACCOUNT'
python infra/azure/reference_assurance.py recover --storage-account $storageAccount --approve-disposable-recovery --output "artifacts/assurance/$runId/recovery.json"
```

The script verifies account/tenant/user context, private-only storage, disabled shared-key access, East US 2, private DNS and pre-existing retention. It creates a random `iyqpis-recovery-<uuid>` container with a 512-byte random probe, verifies its hash, rechecks context and retention, and refuses deletion if ownership metadata or contents changed. It never accepts an existing container name as input. Creation collisions fail without deleting anything.

Before deletion it persists the exact target in the local evidence file. It selects the exact soft-deleted name/version, restores it, compares SHA-256 and measures deletion-to-verified-restore time. Missing versions, ambiguous results and checksum mismatches cannot pass. Successful restore leaves the disposable container available for inspection; failed attempts preserve the last phase and known recovery identifiers. SDK retries and listing waits are bounded. Interruptions can leave a disposable container active or soft-deleted; inspect the checkpoint before taking further action.

## Evidence and cleanup

- Keep generated records under ignored `artifacts/assurance/`; inspect and redact before publishing a reviewed result. No account keys, access tokens or row payloads are written by the tool.
- Record actual execution timestamp, repository commit, runtime versions, resource scope, measured duration, hash result and remaining limitations. Unit-test results must stay labeled simulated.
- After evidence review, an authorized operator can remove only the exact retained `iyqpis-recovery-<uuid>` container. Do not issue wildcard cleanup. Soft-deleted probe data remains billable until retention expires; never shorten account retention just to remove it.
- To resume a failed restore, use the recorded name/version from the checkpoint with the documented Azure container recovery operation. Do not rerun the drill expecting it to restore an earlier run; every invocation creates a fresh isolated target.

References: [container soft delete and HNS support](https://learn.microsoft.com/en-us/azure/storage/blobs/soft-delete-container-overview), [BlobServiceClient container listing/undelete API](https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient?view=azure-python), [existing recovery limits](lenze-recovery.md).
