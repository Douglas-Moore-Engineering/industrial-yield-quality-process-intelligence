# Architecture Decision Records

## Table of contents
- [ADR baseline](#adr-baseline)
- [Decision register](#decision-register)

## ADR baseline

The accepted decisions below govern the pre-Azure architecture. Detailed ADR files may be split out as implementation evolves.

## Decision register

| ADR | Topic | Decision |
|---|---|---|
| ADR-001 | AI authority | Advisory/HITL; no direct control writes |
| ADR-002 | System abstraction | Material/industry-agnostic core with domain adapters |
| ADR-003 | Data foundation | Immutable raw + validated + contextualized + feature/evidence zones |
| ADR-004 | Genealogy | Digital thread is a foundational service, not an analytics add-on |
| ADR-005 | Knowledge representation | Graph capability for relationship-heavy lineage/investigation |
| ADR-006 | Model strategy | Hybrid statistical/ML/physics methods selected by evidence |
| ADR-007 | Twin strategy | Composable digital-twin services with V&V/UQ |
| ADR-008 | Security boundary | Plant control isolated through read-oriented segmented architecture |
| ADR-009 | MLOps | Version code/data/features/models/config; deterministic rollback |
| ADR-010 | Cloud mapping | Defer provider-specific service mapping until sizing and requirement gates complete |

Machine-readable register: [architecture_decisions.csv](../architecture/architecture_decisions.csv)
