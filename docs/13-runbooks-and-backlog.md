# Runbooks and Pre-Azure Implementation Backlog

## Table of contents
- [Required runbooks](#required-runbooks)
- [Implementation backlog](#implementation-backlog)

## Required runbooks

Before production, the system requires:
- data source stale/missing
- timestamp/clock-drift incident
- model degradation/drift
- false-alert spike
- unsafe or implausible recommendation escalation
- model rollback
- feature/schema incompatibility
- OT connectivity outage/store-and-forward recovery
- credential compromise
- evidence/audit export
- digital-twin validation failure/disablement
- plant/site onboarding

## Implementation backlog

### P0
- canonical schemas/data contracts for telemetry, run, material, quality, maintenance, recommendation and outcome
- synthetic/reference dataset preserving temporal and genealogy behavior
- data-quality validation library and timestamp integrity tests
- deterministic event/genealogy reconstruction
- baseline SPC/anomaly pipeline
- first predictive quality/yield benchmark with temporal validation/calibration
- evidence object linking prediction, features, model, data lineage and explanation

### P1
- historical case retrieval
- graph projection for material/product/asset/event relationships
- human disposition workflow and audit model
- drift/calibration/false-alert monitoring
- cloud-agnostic CI/CD and model release manifest
- digital-twin interface contracts and first bounded process surrogate

### P2
- causal analysis after assumptions are documented
- multimodal inspection adapter
- constrained agent-assisted investigation outside the critical prediction path
