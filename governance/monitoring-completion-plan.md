# Reference monitoring completion plan

Status: implementation prepared; deployment and end-to-end verification pending.

Scope: the existing on-demand industrial AI reference environment. No live customer source, online inference service or standing compute is introduced. Production GO remains blocked by the existing source/owner/assurance gaps.

## Proposed changes

- Two Azure Monitor scheduled log alerts, evaluated every five minutes over a fifteen-minute window: job/platform execution failure and structured model/data-health events. Route to the existing operations action group.
- One shared Azure Workbook for job events and data/model/drift observations, linked to the existing private Log Analytics workspace.
- Structured worker telemetry with actual batch data-quality, alert burden, labeled performance, and training-reference range exceedance. Missing labels yield unknown performance. Drift >10% outside training p01-p99 for any feature is explicitly a provisional review signal, not a changed model acceptance threshold.
- Seven-day blob and container soft-delete retention on the existing lake. This is a proposed development retention default, not an approved production RPO/RTO or protection against account deletion.
- New immutable worker image containing monitoring logic and the versioned feature baseline; frozen model and score cutoff unchanged.

## Costs and risks

Scheduled-query alerts have recurring charges; log ingestion, retained deleted data and verification jobs can add usage charges. Existing budget alerts do not cap spending. No new VM, feature-store service or always-on application is proposed. Alert queries can produce false positives until exercised with actual failure events; drift alerts indicate review rather than model invalidity. Deleted data remains billable during retention.

## Required evidence before completion

1. Compile and security-review IaC; inspect incremental deployment previews for unrelated modifications.
2. Query actual ingested console/system logs from a private client. Current workstation queries are correctly rejected by workspace network policy. Preserve private-only access; configure the minimum necessary private verification access rather than opening the workspace.
3. Deploy the reviewed changes and verify enabled alert scopes/actions and dashboard queries.
4. Execute a clearly marked diagnostic failure and confirm rule evaluation and notification delivery through the existing action group. Exclude diagnostic fixtures from model acceptance metrics.
5. Run the frozen model with monitoring enabled; verify log ingestion, alert predicates, labeled and unlabeled behavior, and dashboard output. Historical replay is not a new independent acceptance test.
6. Delete and restore only a uniquely named disposable storage object; compare its checksum. Never use the actual model for a destructive recovery test.
7. Verify registry privacy restored, no unintended active jobs, default data job unchanged, and recorded evidence for every check.

Completion must not be declared from resource existence alone. On-demand idle time is expected; there is no fake live-data freshness or continuous performance claim.

## References

- [Container Apps log schema](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/containerappconsolelogs)
- [System log schema](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/containerappsystemlogs)
- [Container soft delete supports hierarchical namespace](https://learn.microsoft.com/en-us/azure/storage/blobs/soft-delete-container-overview)
