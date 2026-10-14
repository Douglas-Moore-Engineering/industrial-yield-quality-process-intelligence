# IYQPIS Engineering Documentation

**Start here:** [1. Demo](demo.md) → [2. Code walkthrough](code-walkthrough.md) → [3. Results](results.md)

This directory contains the architecture package and deployment evidence for the **Industrial Yield, Quality & Process Intelligence System (IYQPIS)**.

**Azure reference batch deployment: verified.** See [deployment results](azure-validation-results.md) for the successful cloud execution, model metrics and reproducibility evidence.

## Table of contents

1. [Business problem and system mission](01-business-problem-and-mission.md)
2. [Concept of operations and stakeholders](02-conops-and-stakeholders.md)
3. [Requirements and traceability](03-requirements-and-traceability.md)
4. [Data architecture and digital thread](04-data-architecture-and-digital-thread.md)
5. [Integration and interface architecture](integration-and-interface-architecture.md)
6. [AI/ML and decision intelligence architecture](05-ai-ml-and-decision-intelligence.md)
7. [Model validation, V&V and trustworthiness](model-validation-vv-trustworthiness.md)
8. [Security architecture and threat model](06-security-and-threat-model.md)
9. [SLOs, observability and operating model](07-slos-observability-and-operations.md)
10. [Testing, release gates and acceptance](08-testing-release-gates-and-acceptance.md)
11. [Azure entry gate](09-azure-entry-gate.md)
12. [Capacity and performance planning](10-capacity-and-performance-planning.md)
13. [Architecture trade studies](11-architecture-trade-studies.md)
14. [Architecture decision records](12-architecture-decisions.md)
15. [Runbooks and implementation backlog](13-runbooks-and-backlog.md)
16. [Research and standards basis](research-and-standards-basis.md)
17. [Architecture diagrams](architecture/README.md)
18. [Diagram notation standard](DIAGRAM_NOTATION_STANDARD_v0.6.md)
19. [Appendix A — KPI dictionary](appendix-a-kpi-dictionary.md)
20. [Appendix B — Assumptions register](appendix-b-assumptions-register.md)
21. [Appendix C — Reference set](appendix-c-reference-set.md)
22. [Updated DME assurance records](#updated-dme-assurance-records)
23. [Reference evidence review](#reference-evidence-review)

## Current architecture gate

**Pre-Azure Architecture Baseline v0.6**

The v0.6 baseline is the historical cloud-neutral design record. The private Azure reference batch-inference environment is deployed and its frozen benchmark replay is verified. Current state: **G2 reference benchmark PASS; G3 live site shadow not performed; G4/G5 blocked**. Full operational assurance, customer/site acceptance and production authorization remain open. The historical Azure-entry documents are retained for traceability; use [PROJECT_STATUS.md](../PROJECT_STATUS.md) for current deployment status.

## Authority boundary

The initial system is advisory. Existing operational controls and authorized personnel remain authoritative. IYQPIS may observe, predict, explain, simulate and recommend; it may not bypass interlocks, safety systems or existing plant authorization.

## Machine-readable engineering registers

- [Functional requirements](../requirements/functional_requirements.csv)
- [Non-functional requirements](../requirements/nonfunctional_requirements.csv)
- [Requirements traceability](../requirements/traceability.csv)
- [Architecture decision register](../architecture/architecture_decisions.csv)
- [Azure-entry criteria](../governance/azure_entry_criteria.csv)

## Review entry points

- Start with the [root project README](../README.md) for the executive view.
- Use the [architecture diagram index](architecture/README.md) for the 12 GitHub-rendered architecture views.
- Use the numbered documents above for detailed architecture review.

## Updated DME assurance records

- [21-phase lifecycle and gap review](../governance/lifecycle-gap-review.md)
- [Threshold verification register](../governance/threshold-verification.csv)
- [Systems Engineering Management Plan](../docs/systems-engineering-management-plan.md)
- [Standards applicability and assurance](../governance/standards/standards_assurance_summary.md)
- [Customer/site readiness and acceptance boundary](../customer/README.md)

These records are retrospective review/planning artifacts. They do not confer standards-assurance approval, ORR, CAR or production authority.

## Reference evidence review

- [INCOSE implementation map](incose-implementation-map.md)
- [Requirements evidence guide](../requirements/README.md) and [50-row matrix](../requirements/verification_matrix.csv)
- [AI-assisted review findings](../governance/reviews/2026-09-30-reference-review.md)
- [Assurance actions](../governance/reference-assurance-actions.csv) and [organization-control proposal](../governance/organization-controls.md)
- [Azure ML scanner dispositions](../governance/azure-ml-scan-disposition.md), [security/operations implementation review](../governance/reviews/2026-09-30-security-operations.md), and [operational verification runbook](../runbooks/reference-operational-assurance.md)

Mapping coverage is complete; requirement acceptance, independent assurance and customer production are not implied.

## Measurement evidence

- [Versioned measurement index](../governance/measurements/README.md)
- [KPI dictionary](appendix-a-kpi-dictionary.md)
- [Open KPI measurement plans](../governance/measurements/planned-kpis.md)

The index connects the README results to original evidence, evaluated versions, limitations and existing acceptance decisions. Measurement, criterion result and authorized acceptance remain separate.

