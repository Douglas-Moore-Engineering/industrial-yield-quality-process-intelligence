# Pre-Azure Gate Status

> **Historical v0.6 pre-Azure design record.** The dated design text below is retained for traceability. It is not the current deployment decision or inventory. Operational status is superseded by [PROJECT_STATUS.md](../PROJECT_STATUS.md) and [Azure execution evidence](../docs/azure-validation-results.md).
>
> Reviewed 2026-09-30: a bounded private Azure development/reference environment has been deployed and exercised. This does not close customer/site production-entry criteria, grant production approval, or retroactively approve historical pending gates. Build Production AI Systems v9 §13 permits a bounded reference environment while customer/site assumptions remain explicit and production use remains gated.


This register distinguishes architecture artifacts that are complete now from evidence that requires pilot data, stakeholder approval, or runtime testing.

| Gate | Status | Current evidence / blocker |
|---|---|---|
| AZ-G01 Canonical schemas/data contracts versioned | **Complete for architecture baseline** | Seven versioned cloud-neutral JSON Schemas under `data/contracts/`; production adoption still requires source-owner mapping and contract tests |
| AZ-G02 Event-rate and retention measurements | Pending | Requires pilot/source profiling |
| AZ-G03 Latency and warning-horizon requirement | Pending | Requires process timing and pilot acceptance discussion |
| AZ-G04 OT trust boundary / allowed flows | Architecture complete; approval pending | Trust-zone design exists; site/OT approval requires actual environment |
| AZ-G05 Identity roles / authorization matrix | Partial | Stakeholder authority model exists; enterprise IAM mapping pending |
| AZ-G06 Data classification / retention | Pending | Requires client/data-owner policy |
| AZ-G07 Model release/evidence manifest | Architecture defined; implementation pending | MLOps/evidence requirements defined |
| AZ-G08 RPO/RTO / availability targets | Pending | Requires operational criticality and deployment context |
| AZ-G09 Pilot acceptance thresholds | Pending | Must be derived from baseline data |
| AZ-G10 Trade studies / ADRs accepted | **Complete for pre-Azure baseline** | TS-01–TS-09 and ADR-001–ADR-010 documented |
| AZ-G11 Threat model reviewed | Architecture complete; stakeholder review pending | Threat register and controls documented |
| AZ-G12 Cost-model inputs measured | Pending | Requires workload/profile evidence |

## Decision

**Azure architecture mapping may begin as a design exercise, but provisioning and SKU commitment remain gated by the pending evidence above.**
