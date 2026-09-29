# On-demand development data engineering

## Verified implementation and scope

The private ADLS Gen2 lake and four containers already exist. This release adds a replayable batch implementation. **The network and job deployments succeeded, and live Azure acceptance passed for all five sample datasets: 1,104,500 validated records and 16 artifacts.** Full replay produced the same run ID. An independent read-only probe re-read the remote manifest and every artifact, verified their checksums, and confirmed all blob modification times predated replay. The registry and lake remain private. No automatic schedule is configured.

- Five sample adapters emit telemetry, quality and maintenance contracts. Seven schemas enforce required fields, types and a timezone-aware date-time profile (no leap seconds).
- `iyqpis.pipeline` streams records, detects duplicate event IDs per dataset, rejects invalid/nonfinite records, and leaves failed attempts under `.pending-*` without a completion manifest.
- `validated` retains BAD/UNCERTAIN readings; `contextualized` contains per-asset/tag/unit summaries using only GOOD readings. Distinct events at equal timestamps are retained. Historical out-of-order records are counted against the stream high-water mark, not silently sorted.
- `curated-evidence` contains quality counts. A manifest binds inputs, schema/code hashes, fixed ingest time, output counts and checksums. Source files are rechecked before local publication. Repeating the same inputs/code/time verifies and reuses the existing run; corruption fails closed.
- `iyqpis.azure_batch` reads existing raw blobs with ETag conditions, authenticates only through managed identity, requires private DNS, writes versioned output prefixes without overwrite, reads outputs back to verify their hashes, then writes the completion manifest last. Retrying interrupted publication verifies existing bytes. No raw data is written by this job.

This is sample-data engineering. Stream summaries do not reconstruct missing material/run genealogy. Synthetic timestamps and assumed UTC are declared in the adapters. Production source mapping, freshness limits, approved quality thresholds, retention, backup/recovery and plant integration still require actual source-owner evidence. A local run does not prove private Azure access.

## Local operation

```powershell
python -m pip install -r requirements-dev.txt
$env:PYTHONPATH = 'src'
python -m iyqpis.pipeline data/samples/raw artifacts/data-runs --ingest-time 2026-09-28T00:00:00Z
# Use --dataset manufacturing-spc for the small reference batch.
python -m pytest -q
```

Keep the ingest timestamp unchanged for retry/replay. Changing source, code, schemas or timestamp deliberately creates a new run. Artifacts are ignored by Git. Never place outputs under the raw root. Failed local attempts can be inspected before removing their individually identified staging directory; do not delete a whole lake/container to retry.

Read Azure outputs only through `curated-evidence/runs/<run-id>/manifest.json`. Manifest artifact paths begin with a container name: the remainder maps to `<container>/runs/<run-id>/<relative-path>`. A prefix with no manifest is uncommitted and must not be consumed. Code prevents overwrites, but output RBAC is not a WORM/immutability guarantee.

## Azure release and operation

1. **Network:** `infra/data-network.bicep` adds `snet-data-jobs` (10.80.2.0/27), its NSG, and an HTTPS allow rule into existing endpoints. No existing subnet, data service or endpoint is redeployed. Dependency egress is limited to documented Azure service tags, private endpoints, intra-subnet traffic and DNS. There is no job ingress.
2. **Preserve configuration:** before network activation, add `dataJobSubnetPrefix: {value: '10.80.2.0/27'}` to the ignored foundation parameters and future CI parameter secret. The foundation and CI templates now support this option. Omitting it on a later foundation redeployment would remove the declaration of the added subnet/rule; never approve such a preview.
3. **Image:** build `docker build -f infra/data/Dockerfile -t iyqpis-data:review .`. The context excludes raw data, account settings and credentials. The image runs as UID 10001. Publish to the existing ACR through an authorized private-connected builder, and use the resulting repository `@sha256:` digest. The laptop build and approved registry image publication passed. Connectivity inspection found no Windows VPN profiles, platform routes, Azure gateway/peering/build VM/ACR agent pool, or GitHub self-hosted runners; registry/lake DNS resolves outside the platform private subnet. Do not enable public ACR/storage access as an implicit workaround.
4. **Job:** `infra/data-job.bicep` references the existing lake, registry and logs. It adds an internal Consumption environment, manual job, dedicated managed identity, raw-container Reader, Contributor on the three output containers, AcrPull, and diagnostics. No shared keys or client secrets. Job configuration: 2 vCPU/4 GiB, one replica, 3600-second attempt timeout, one retry, no schedule.
5. **Operator deployment:** copy `data-job.parameters.example.json` to an ignored `.local.json`, populate existing names/subnet and the published digest. After the network is ready, run `Invoke-DataJob.ps1 -Action Preview`; inspect the ignored full preview. Its first-deployment guard rejects changes/deletions of existing resources. Deploy only the reviewed release with `-Action Deploy -ApproveDeployment`.
6. **On demand:** use `Invoke-DataJob.ps1 -Action Start -ApproveRun` and `-Action Status`. Start refuses a known active/unresolved execution; this is an operator check, not a distributed lock. Identical concurrent batches still use no-overwrite writes and checksum verification. The configured input snapshot time and dataset selection stay fixed for replay. Review job configuration before a new snapshot.

No GitHub OIDC activation is needed for the guarded local operator path. GitHub's existing licensing/protection blocker remains separate.

To run all five datasets, use the complete execution-template override exposed by the operator script:

```powershell
./infra/azure/Invoke-DataJob.ps1 -Action Start -ApproveRun -Datasets manufacturing-spc,ai4i-2020-predictive-maintenance,bosch-injector-eol,secom,steel-plates-faults
./infra/azure/Invoke-DataJob.ps1 -Action Status
```

Repeat the same command for replay. The default job still selects the small manufacturing-SPC dataset. The installed CLI ignored inline `--env-vars` overrides during acceptance; the script therefore supplies the entire template through `--yaml`, preserving image, resources and identity environment. Its ignored JSON template is valid YAML. Verify the execution's actual DATASETS value before interpreting a run as full-data acceptance.

## Costs and approval

East US 2 retail rates retrieved on 2026-09-28: USD 0.000024/vCPU-second and 0.000003/GiB-second. A 2-vCPU/4-GiB job is USD 0.216 per active hour, or USD 0.108 per 30-minute attempt, before free grants. The configured timeout plus one retry allows up to two attempt-hours (USD 0.432 compute) per execution, excluding provisioning/retry overhead, storage requests/capacity, logs and applicable networking costs. This is an estimate, not a billing cap. Multiple manual executions multiply cost. Existing registry/endpoints/storage continue charging when the job is idle.

The on-demand release, stated compute costs and temporary single-IP registry publishing window were explicitly approved. Live executions confirmed Microsoft.App capacity and private image access. The job remains Manual with a 3600-second attempt timeout, one retry and Consumption compute; existing platform services continue billing when job compute is idle.

### Approved one-time registry publishing window

`Publish-DataImage.ps1` is prepared as an alternative to provisioning a VPN/private builder. It requires `-ApproveTemporaryRegistryAccess` and the operator's single public IPv4 address. It checks the registry starts private-only, default-deny, with no IP rules and admin authentication disabled; allows only that /32, temporarily enables the public endpoint, authenticates using Azure CLI, pushes the local image, and stores its immutable digest in ignored parameters. Its `finally` block disables public access, removes the exact temporary rule and verifies restoration. Storage remains private throughout.

This deliberately relaxes registry network exposure during publication; approval was received. The image was published and the registry was verified restored to Disabled with zero IP rules and admin authentication disabled. The first cleanup check exposed Azure CLI normalization of /32 rules to bare IP addresses; cleanup was corrected and the simulated tests now cover that behavior. Authentication remains required. If the client loses power or is killed, `finally` cannot run: immediately disable the registry public endpoint and remove that exact /32 rule in Azure Portal, then verify Disabled/no IP rules/admin disabled. There is no automatic TTL on the network rule. Four simulated guard tests verify no action without approval and restoration after success, push failure and an ambiguous enable timeout; they cannot guarantee cleanup after machine termination.

## Acceptance and recovery

- Local evidence: 44 pytest cases passed; full five-dataset run validated 1,104,500 records, producing 10 validated files, five stream summaries and one quality report. Six Bicep entrypoints compile. Checkov: 46 passed, zero failed, three existing exceptions. Docker build and isolated non-root manufacturing-SPC run passed (2,700 validated records).
- Additive network Azure what-if: three Create, 44 Ignore, zero Modify/Delete. Full-foundation preview is not the network release artifact.
- Job Azure what-if: nine Create, 44 Ignore, zero Modify/Delete. Both additive deployments are Succeeded. The image is published by immutable digest; registry public access was restored to Disabled with zero temporary IP rules.
- Live acceptance on 2026-09-28: reference run passed (four artifacts); full run and replay passed (16 artifacts, run `cb03fc7d2f32c0e29031cc4fd00fc4fb`). `verify-data-run.py`, executed inside the private environment using the existing managed identity, independently verified 1,104,500 validated records across five datasets, every artifact checksum, and unchanged artifact/manifest modification times after replay. It performs no writes. Detailed execution responses and logs are kept in ignored `.local.json`/`.local.log` files.
- Live platform controls passed, including private endpoints/DNS, registry access, monitor configuration, operational alerts and budget. Console logs are accessible. Persisted Log Analytics arrival and a deliberately failed cloud execution were not tested in this acceptance; pipeline-specific automatic paging remains unconfigured. Earlier email test delivery was separately confirmed.
- Operator regression checks passed for approval refusal, Azure region display-name normalization, complete execution-template preservation, and refusal while another execution is active. Inline environment overrides were ignored by the installed CLI; the full/replay evidence comes from the corrected template overrides, not the earlier reference-only runs.
- For failed execution, inspect its status and Container Apps console/system logs. Application logs contain failure type, not raw records or credentials. Re-run the same immutable image/input timestamp after correcting the cause; uncommitted prefixes are ignored until a valid manifest is written. Pipeline-specific automatic paging is not configured; the operator checks every manual execution.

## References

- [Container Apps jobs](https://learn.microsoft.com/en-us/azure/container-apps/jobs)
- [Consumption billing](https://learn.microsoft.com/en-us/azure/container-apps/billing)
- [Network dependency rules](https://learn.microsoft.com/en-us/azure/container-apps/firewall-integration)
- [Container Apps log routing](https://learn.microsoft.com/en-us/azure/container-apps/log-options)
- [Private registry connectivity](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-private-link)

## Current deployment checkpoint

On 2026-09-28 Azure CLI session refresh was initially rejected with AADSTS530035. Browser sign-in restored access without disabling directory security defaults. Both network and `iyqpis-dev-data` deployments are Succeeded. Reference, full-data and replay runs passed, followed by independent read-only remote verification. The registry and lake remain private. Do not redeploy an already completed environment merely because a client polling session failed.
