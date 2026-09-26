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
10. [Architecture diagrams](architecture/README.md)
11. [Diagram notation standard](DIAGRAM_NOTATION_STANDARD_v0.6.md)

## Current architecture gate

**Pre-Azure Architecture Baseline v0.6**

The architecture is deliberately cloud-agnostic at this point. Azure service selection, landing-zone design, network topology, sizing, cost modeling and IaC begin only after the Azure-entry evidence gates are satisfied.

## Authority boundary

The initial system is advisory. Existing operational controls and authorized personnel remain authoritative. IYQPIS may observe, predict, explain, simulate and recommend; it may not bypass interlocks, safety systems or existing plant authorization.
