# Requirements and Traceability

## Table of contents

- [Requirement model](#requirement-model)
- [Functional requirements](#functional-requirements)
- [Non-functional requirements](#non-functional-requirements)
- [Traceability](#traceability)
- [Acceptance philosophy](#acceptance-philosophy)

## Requirement model

Requirements are maintained as versioned engineering records and linked to business needs, architecture decisions, verification methods, evidence and release gates.

## Functional requirements

The authoritative list is [functional_requirements.csv](../requirements/functional_requirements.csv), covering FR-001 through FR-030.

Major capability groups:
- industrial telemetry ingestion
- production/material/quality context
- material and product genealogy
- process-health and stability indicators
- predictive quality and yield risk
- anomaly/change-point/drift detection
- explainability and root-cause intelligence
- counterfactual and digital-twin analysis
- downstream exposure tracing
- operator alerting and human disposition
- evidence and model lineage
- rollback and drift monitoring
- industrial knowledge graph
- separation of advisory AI from operational control

## Non-functional requirements

The authoritative list is [nonfunctional_requirements.csv](../requirements/nonfunctional_requirements.csv), covering NFR-001 through NFR-020.

Major quality attributes:
- availability
- safety
- latency
- reliability
- explainability
- traceability
- security
- integrity
- auditability
- scalability
- interoperability
- observability
- recoverability
- maintainability
- portability
- data quality
- human factors
- time integrity
- governance
- fail-safe behavior

## Traceability

See [traceability.csv](../requirements/traceability.csv).

The chain is:

`Business need → stakeholder requirement → system requirement → architecture element → verification method → KPI/evidence → release gate`

## Acceptance philosophy

A dashboard or model metric alone is not acceptance. A pilot must demonstrate data reconstruction, calibrated prediction, actionable warning horizon, traceability, safe failure, model rollback, evidence lineage, human decision capture and agreed operational usefulness.
