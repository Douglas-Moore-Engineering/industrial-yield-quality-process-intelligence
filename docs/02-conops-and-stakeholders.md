# Concept of Operations and Stakeholders

## Table of contents

- [Operating concept](#operating-concept)
- [Authority model](#authority-model)
- [Primary stakeholders](#primary-stakeholders)
- [Operational scenarios](#operational-scenarios)
- [Degraded mode](#degraded-mode)

## Operating concept

IYQPIS operates alongside existing plant systems and is initially advisory. It consumes controlled data exports from process, quality, production and maintenance systems; it does not become a prerequisite for safe plant operation.

## Authority model

`AI recommendation → policy validation → authorized human review → existing approved operational procedure`

The initial system may:
- observe
- contextualize
- detect
- predict
- explain
- simulate
- recommend

The initial system may not:
- change PLC logic
- override interlocks
- bypass safety systems
- directly change machine setpoints
- suppress required quality controls
- autonomously dispatch maintenance

## Primary stakeholders

| Stakeholder | Primary concern |
|---|---|
| Plant manager | yield, throughput, quality, loss |
| Production manager | stable execution and intervention priority |
| Process engineer | process drivers, operating envelope, counterfactuals |
| Quality engineer | conformance, defect risk, containment |
| Operator | clear, actionable and low-noise alerts |
| Maintenance / reliability | equipment contribution to process risk |
| Materials engineer | lot/batch effects and material behavior |
| Controls / OT engineer | safe integration and control boundaries |
| Data engineer | data contracts, quality, timing, lineage |
| ML engineer | model V&V, drift, deployment and rollback |
| AI / systems architect | integration, scalability, governance and resilience |
| Cybersecurity | segmentation, identity, integrity and evidence |
| Governance / audit | accountability, traceability and approvals |

## Operational scenarios

1. **Emerging yield degradation** — multivariate behavior indicates rising quality risk before conventional alarms fire.
2. **Material-driven quality shift** — a within-spec material lot exhibits different behavior under a specific operating envelope.
3. **Hidden process drift** — the process gradually leaves the validated multivariate region.
4. **Quality-failure investigation** — engineers reconstruct the complete material/process/equipment trajectory.
5. **Modernization / commissioning** — distribution shift causes the model to abstain rather than silently extrapolate.
6. **Throughput/yield tradeoff** — a validated simulation estimates the impact of a proposed operating change.
7. **Equipment-quality interaction** — maintenance and asset-health data are evaluated as contributors to quality loss.
8. **Containment** — exposed downstream material is traced from an identified excursion.

## Degraded mode

If IYQPIS becomes unavailable, existing plant operating procedures remain in force. AI failure must not stop basic production or create unsafe control behavior.
