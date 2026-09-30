# INCOSE learning-to-implementation map

This interpretive mapping uses the INCOSE Systems Engineering Handbook, fifth edition, Chapters 1–6 discussed during the project review. It is not a clause-level assessment, certification or claim that every handbook topic is implemented. Source repository reviewed: `cc911d091323831f11f7c889a20514312d4387f8`, 2026-09-30. Current evidence scope is a pre-customer industrial AI reference system.

## Contents

- [Chapter mapping](#chapter-mapping)
- [Concrete authority trace](#concrete-authority-trace)
- [Scope and remaining evidence](#scope-and-remaining-evidence)

## Chapter mapping

| Chapter | Application | Repository evidence | Limit |
|---|---|---|---|
| 1: systems concepts | Whole manufacturing state, stakeholders, boundaries and degraded operation | [Mission](01-business-problem-and-mission.md); [ConOps](02-conops-and-stakeholders.md) | Business targets and site constraints await an authorized baseline |
| 2: lifecycle/processes | Stable requirements, verification, release progression and acceptance boundaries | [Requirements](../requirements/README.md); [gates](08-testing-release-gates-and-acceptance.md); [SEMP](systems-engineering-management-plan.md) | Management/assurance review pending; no customer ORR/CAR |
| 3: analyses/methods | Contracts, trade studies, integrity, reproducible decisions and recovery | [Trade studies](11-architecture-trade-studies.md); [verification](../src/iyqpis/lenze_verification.py); [recovery](../runbooks/lenze-recovery.md) | Local artifact recovery is not cloud recovery; graph/twin/causal capabilities remain design intent |
| 4: tailoring | Bounded manual batch scope, versioned feature files and deferred site gates | [Tailoring](../governance/standards/lifecycle_tailoring_record.md); [feature governance](../features/README.md) | Retrospective rationale is not stakeholder approval |
| 5: professional practice | Role concerns, attributable local decisions and explicit evidence limitations | [Ledger](../src/iyqpis/operations.py); [organization proposal](../governance/organization-controls.md) | Actor strings are not authenticated identities; competence, inclusive participation and independent review need actual records |
| 6: case-study lessons | Authority protection, interface coordination, artifact integrity, maintainability and bounded use | [Security](06-security-and-threat-model.md); [interfaces](integration-and-interface-architecture.md); [reference tests](../tests/test_intelligence.py) | Analogies illustrate engineering judgment; they do not establish safety certification or plant readiness |

## Concrete authority trace

Stakeholder need SR-03 → FR-030 / NFR-002 / NFR-020 → advisory ConOps and ADR-001/008 → reference `infer`, `Ledger.activate`, `Ledger.review` and `production_gate` → tests for shadow authority, production activation refusal and self-asserted readiness flags. The [verification matrix](../requirements/verification_matrix.csv) records exact paths and remaining acceptance work.

The general reference shadow implementation differs from the Lenze frozen-batch implementation. Checks and metrics must be attributed to the path that contains them. Lenze reference replay verifies frozen decisions with publisher precomputed features; it does not establish calibrated plant probabilities, a live shadow trial or independent confirmation data.

## Scope and remaining evidence

The architecture's copper rod/wire scenario remains illustrative. The passing benchmark is the Lenze reference; earlier SECOM work has separate limitations. The teaching example of reducing defects from 6% to 4% is not a project requirement or observed result. Approved business targets require an actual operating baseline.

See the [completed AI-assisted repository review](../governance/reviews/2026-09-30-reference-review.md) for inspection results and the [assurance actions](../governance/reference-assurance-actions.csv) for unresolved work. Missing customer acceptance is a stage boundary, not a reason to invent customer evidence.
