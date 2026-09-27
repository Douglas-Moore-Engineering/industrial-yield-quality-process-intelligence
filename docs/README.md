# IYQPIS Engineering Documentation

This directory is the authoritative pre-Azure architecture package for the **Industrial Yield, Quality & Process Intelligence System (IYQPIS)**.

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

## Current architecture gate

**Pre-Azure Architecture Baseline v0.6**

The architecture is deliberately cloud-agnostic at this point. Azure service selection, landing-zone design, network topology, sizing, cost modeling and IaC begin only after the Azure-entry evidence gates are satisfied.

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
