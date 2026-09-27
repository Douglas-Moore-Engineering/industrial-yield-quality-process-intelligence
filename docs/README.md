# IYQPIS Engineering Documentation

This directory is the authoritative pre-Azure architecture package for the **Industrial Yield, Quality & Process Intelligence System (IYQPIS)**.

## Table of contents

1. [Business problem and system mission](01-business-problem-and-mission.md)
2. [Concept of operations and stakeholders](02-conops-and-stakeholders.md)
3. [Requirements and traceability](03-requirements-and-traceability.md)
4. [Data architecture and digital thread](04-data-architecture-and-digital-thread.md)
5. [AI/ML and decision intelligence architecture](05-ai-ml-and-decision-intelligence.md)
6. [Security architecture and threat model](06-security-and-threat-model.md)
7. [SLOs, observability and operating model](07-slos-observability-and-operations.md)
8. [Testing, release gates and acceptance](08-testing-release-gates-and-acceptance.md)
9. [Azure entry gate](09-azure-entry-gate.md)
10. [Capacity and performance planning](10-capacity-and-performance-planning.md)
11. [Architecture trade studies](11-architecture-trade-studies.md)
12. [Architecture decision records](12-architecture-decisions.md)
13. [Runbooks and implementation backlog](13-runbooks-and-backlog.md)
14. [Architecture diagrams](architecture/README.md)
15. [Diagram notation standard](DIAGRAM_NOTATION_STANDARD_v0.6.md)
16. [Appendix A — KPI dictionary](appendix-a-kpi-dictionary.md)
17. [Appendix B — Assumptions register](appendix-b-assumptions-register.md)
18. [Appendix C — Reference set](appendix-c-reference-set.md)

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
