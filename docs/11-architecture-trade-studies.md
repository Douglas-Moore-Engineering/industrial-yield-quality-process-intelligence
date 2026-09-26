# Architecture Trade Studies

## Table of contents
- [Decision summary](#decision-summary)
- [Trade studies](#trade-studies)

## Decision summary

The current baseline makes cloud-agnostic architectural decisions without prematurely selecting implementation products.

## Trade studies

| Study | Decision | Rationale |
|---|---|---|
| TS-01 Stream vs batch | Hybrid | Streaming for operational risk; batch for history/training |
| TS-02 Edge vs centralized inference | Hybrid | Edge/near-edge only where latency/resilience justify it; centralized governance/training |
| TS-03 Relational-only vs graph | Polyglot | Lake/relational for facts; graph for genealogy and relationship-heavy investigation |
| TS-04 Pure ML vs physics-ML | Hybrid where feasible | Physical constraints improve validity, extrapolation and explanation |
| TS-05 Global vs site-specific models | Hierarchical | Reusable global features with line/site validation and local calibration |
| TS-06 Direct control vs advisory | Advisory | Human authority minimizes unsafe control coupling |
| TS-07 Monolithic vs composable digital twin | Composable | Enables independent verification, reuse and replacement |
| TS-08 LLM in prediction path vs investigation only | Investigation only | Keep generative AI outside safety/quality-critical numeric prediction path |
| TS-09 Tightly coupled cloud vs portable core | Portable core | Use managed services later while preserving canonical contracts and exportable evidence |
