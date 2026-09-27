# Canonical Data Contracts

These cloud-neutral contracts establish the minimum shared semantics needed before Azure service mapping.

## Contract set

| Contract | Purpose |
|---|---|
| [telemetry.schema.json](telemetry.schema.json) | time-series process/asset observation |
| [production_run.schema.json](production_run.schema.json) | production order/run/campaign context |
| [material_lot.schema.json](material_lot.schema.json) | material identity and genealogy |
| [quality_result.schema.json](quality_result.schema.json) | quality/lab/inspection result and disposition |
| [maintenance_event.schema.json](maintenance_event.schema.json) | maintenance and asset intervention event |
| [recommendation.schema.json](recommendation.schema.json) | AI advisory recommendation and evidence linkage |
| [decision_outcome.schema.json](decision_outcome.schema.json) | authorized human disposition and realized outcome |

## Contract rules

- JSON Schema draft 2020-12.
- Semantic schema version is explicit.
- Event time and ingestion time are separate.
- Source system and plant identity are retained.
- Source observations remain distinct from model recommendations and human decisions.
- Contracts are intentionally generic; site-specific fields require controlled extension rather than silent schema drift.
- Production adoption requires contract tests, data-owner review, identifier mapping and retention/classification approval.
