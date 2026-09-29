# Operations release evidence

Updated 2026-09-28. The development foundation and **operations release are deployed**. CI federation remains disabled; private-client acceptance is blocked by VM-family quota.

| Check | Result |
|---|---|
| Bicep compilation | `main.bicep`, `operations.bicep`, `foundation-ci.bicep`, `probe.bicep`: exit 0, no warnings |
| Azure operations validation | Succeeded, error null |
| Azure operations what-if | **8 to create, 32 to ignore**; no modifications/deletions |
| Azure operations deployment | `iyqpis-dev-operations`: Succeeded; budget, action group, four alerts, Activity Log export and unprivileged deployer identity |
| Live operations verification | Passed: budget thresholds/recipient, four routed alerts, eight Activity Log categories, unprivileged/unfederated CI identity, zero probe resources |
| Alert delivery | Passed: user confirmed receipt of the new Azure test email after receiver verification; Azure test state Complete, receiver status Succeeded, CLI exit 0 |
| GitHub activation | Required reviewers rejected (HTTP 422); branch protection unavailable (HTTP 403); no federation or deployment role |
| Quota request | Microsoft.Quota registered; request for two standardBsv2Family vCPUs in East US 2 failed: QuotaNotAvailableForResource |
| Live private probe | Preflight QuotaExceeded: standardBsv2Family limit 0, required 2; cleanup verified, no probe resources remain |
| Local deployment safety | 12 cases passed |
| CI deployment safety | 9 cases passed |
| Private probe mocked safety | 4 Python unit tests passed; this is not a live probe run |
| Temporary SSH key generation | Passed; temporary keys removed |
| Privacy scan | No configured account/tenant/subscription identifiers outside ignored local files |
| Formatting | `git diff --check`: exit 0 |

Actual Checkov 3.3.20 output (`checkov -d infra/ --framework bicep --compact --quiet`, exit 0):

```text
Passed checks: 34, Failed checks: 0, Skipped checks: 1
```

The skip is the previously documented registry quarantine exception, pending a real image scan/release workflow. No new security exception was added for the probe; VM extension installation is disabled, host encryption and Trusted Launch enabled.

Live read-only acceptance passed for the current foundation: expected account context, Key Vault RBAC/private access/purge protection, registry private access/local-auth settings, three approved endpoints and DNS groups, seven completed DNS links, private Monitor query/ingestion with local authentication disabled, service diagnostic routing, and registry-scoped publisher/runtime role assignments. This does not prove private DNS resolution from a client, image pull, alert delivery, log arrival or backup restoration.

The small probe SKU supports host encryption and non-zonal deployment is not listed as restricted. EncryptionAtHost was registered. Allocation preflight failed with zero VM-family quota; no compute remains. Public Linux retail rate queried: USD 0.0416/hour plus temporary disk/diagnostics storage. Resource-group Cost Management query returned no posted rows, not a zero-cost guarantee.

## Skill completion self-check

- PASS: all generated Bicep entrypoints compile; command output recorded above.
- PASS WITH EXISTING EXCEPTION: Checkov has no failed checks; one documented quarantine skip.
- PASS (static): private access retained, scoped identity, no embedded credentials, secure alert parameter, no public probe IP, password login/extensions disabled, protected boot and encryption, cleanup and shutdown fallback prepared.
- PASS: existing foundation referenced by operational templates; Azure preview proposes no modifications/deletions to it. CI updates are a separate explicitly reviewed future workflow.
- PASS: IaC under `infra/`; original source diagrams and governance baseline retained; personal identifiers stay in ignored local files.
- PASS: user approval received; operations deployment succeeded; EncryptionAtHost registered; failed probe cleanup verified.
- PENDING: compute quota and live private probe, GitHub supported branch/environment protection and successful OIDC workflow run. No automated deployment trust was granted.

Full Azure inventory, parameters and preview are ignored local evidence files. See [operating procedure](OPERATIONS.md) for next actions and recovery steps.
