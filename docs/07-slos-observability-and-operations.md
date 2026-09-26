# SLOs, Observability and Operations

## Table of contents

- [Observability model](#observability-model)
- [SLO categories](#slo-categories)
- [Alerting principles](#alerting-principles)
- [Operational response](#operational-response)
- [Capacity planning](#capacity-planning)

## Observability model

Observe the complete chain:

`source → ingestion → validation → contextualization → feature service → model → decision API → human disposition → outcome`

## SLO categories

- source freshness
- ingestion completeness
- pipeline availability
- prediction availability
- decision latency
- genealogy completeness
- evidence persistence
- model calibration
- false-alert burden
- drift-detection latency
- rollback/recovery time

Numeric targets are established from process-response needs and measured workload, not invented in advance.

## Alerting principles

Alerts must be actionable, severity-aware and budgeted. Alert fatigue is treated as a reliability failure.

## Operational response

`detect breach → page/notify → triage runbook → degraded/abstain mode → rollback/recover → incident record → post-incident review → corrective action`

## Capacity planning

Sizing inputs include:
- event rate
- average event size
- burst factor
- retention
- feature expansion factor
- concurrency
- training window
- model size
- inference latency target
- number of lines/plants/assets

Azure sizing is deferred until these inputs are measured.
