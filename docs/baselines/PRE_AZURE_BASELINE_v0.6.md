# Pre-Azure Architecture Baseline v0.6

## System
**Industrial Yield, Quality & Process Intelligence System (IYQPIS)**

## Mission
Detect emerging process instability, predict yield and quality risk before material becomes unrecoverable, trace affected material through the production lifecycle, identify likely contributing conditions, evaluate bounded corrective actions, and provide evidence-backed recommendations to authorized operators and engineers.

## Scope
The platform is industry-agnostic. Copper manufacturing is a validation scenario, not a permanent boundary.

## Authority model
Initial deployment is advisory:
- Observe
- Contextualize
- Predict
- Explain
- Recommend
- Authorize through policy and human review
- Verify
- Learn

AI has no direct PLC, DCS, SCADA, SIS, or safety-system write authority.

## Architecture planes
1. **Plant / OT plane** — sensors, PLC/DCS, historian, MES, quality systems, maintenance systems.
2. **Industrial intelligence plane** — ingestion, validation, contextualization, digital thread, genealogy, feature/model services, predictive quality, yield risk, anomaly/drift, root-cause intelligence, counterfactuals, digital twin.
3. **Governance / operations plane** — policy guardrails, HITL, evidence ledger, MLOps, security, observability, SLOs, rollback and auditability.

## Core business outcomes
- Increase first-pass and material yield.
- Reduce scrap, rework and cost of poor quality.
- Reduce detection and diagnosis latency.
- Improve product/material genealogy and containment.
- Preserve throughput, safety and equipment protection.
- Improve modernization/ramp-up stability.

## Core stakeholders
Plant management, production, process engineering, quality, operators, maintenance, reliability, materials, controls/OT, data engineering, ML engineering, AI architecture, cybersecurity, governance, operations leadership and sustainability.

## Data domains
- material
- production
- asset/equipment
- telemetry
- process state
- product
- quality
- maintenance
- operator actions
- models/predictions
- alerts
- recommendations
- decisions/outcomes

## Functional baseline
See `requirements/functional_requirements.csv` for FR-001 through FR-030.

## Non-functional baseline
See `requirements/nonfunctional_requirements.csv` for NFR-001 through NFR-020.

## Traceability
See `requirements/traceability.csv`.

## Architecture decisions
See `architecture/architecture_decisions.csv`.

## Security baseline
- segmented OT/IT trust zones
- read-oriented plant export path
- least privilege
- evidence integrity
- signed/versioned model artifacts
- no direct AI control writes
- fail-safe degraded mode
- deterministic rollback
- full auditability

## MLOps baseline
- version data, features, code, configuration and models
- temporal validation
- calibration and drift monitoring
- release evidence manifests
- shadow deployment
- advisory canary
- production advisory
- rollback and incident recovery

## Release gates
- G0 data readiness
- G1 reproducible baseline
- G2 offline validation
- G3 shadow
- G4 advisory canary
- G5 production advisory
- later autonomy only after separate safety validation

## Azure entry
Azure mapping begins only after the criteria in `governance/azure_entry_criteria.csv` are satisfied.

## Diagrams
Editable Mermaid sources are under `docs/diagrams/` and follow the v0.6 notation standard:
- 8.5 × 11 portrait when rendered
- white background
- consistent swim lanes
- curved connectors
- correct exclusive merge and parallel gateway semantics
