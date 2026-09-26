# Industrial Yield, Quality & Process Intelligence System (IYQPIS)

Enterprise industrial AI architecture for predicting, explaining, tracing, and helping prevent yield loss, quality deviations, and process instability in continuous and discrete manufacturing environments.

## Current maturity

**Pre-Azure Architecture Baseline v0.6**

The repository is intentionally cloud-agnostic at this gate. No Azure services, regions, SKUs, subscriptions, network resources, or IaC have been selected or provisioned.

## Mission

Shift industrial operations from late defect detection toward governed, evidence-backed early warning and intervention:

`Observe → Contextualize → Predict → Explain → Recommend → Authorize → Verify → Learn`

The initial operating model is advisory. Existing plant controls and authorized personnel retain decision and execution authority.

## Architecture principles

- Manufacturing continuity is independent of AI availability.
- OT safety and control systems remain authoritative.
- Quality and yield are modeled from the complete manufacturing state: material, process, equipment, production, maintenance, environment, and history.
- Material/product genealogy and evidence lineage are first-class platform capabilities.
- Human approval and policy guardrails precede authorized operational action.
- Model/data drift, abstention, rollback, auditability, and traceability are mandatory production capabilities.
- Core platform contracts remain industry-neutral; copper is a validation scenario, not a permanent platform boundary.

## Repository map

| Path | Purpose |
|---|---|
| `docs/baselines/` | Formal architecture baseline and PDF |
| `docs/diagrams/` | Architecture diagrams and editable Graphviz sources |
| `docs/reviews/` | Diagram review package |
| `requirements/` | Functional, non-functional, and traceability records |
| `architecture/` | Architecture decision records/register |
| `governance/` | Azure-entry and governance gates |
| `data/contracts/` | Canonical industrial data contracts (next phase) |
| `src/` | Production implementation (intentionally empty pre-Azure) |
| `infra/azure/` | Azure architecture/IaC (next phase) |
| `tests/` | Verification and validation assets |
| `runbooks/` | Operational recovery/incident procedures |
| `tools/diagramming/` | Diagram-generation utilities |

## Current baseline artifacts

- `docs/baselines/IYQPIS_PreAzure_Architecture_Baseline_v0.6.docx`
- `docs/baselines/IYQPIS_PreAzure_Architecture_Baseline_v0.6.pdf`
- `docs/reviews/IYQPIS_Diagram_Review_v0.6.docx`
- `docs/reviews/IYQPIS_Diagram_Review_v0.6.pdf`
- `docs/DIAGRAM_NOTATION_STANDARD_v0.6.md`

## Next architecture gate

Azure architecture mapping begins only after the pre-Azure baseline is accepted. The next phase will map cloud-agnostic capabilities to Azure services, define landing-zone/network/topology choices, complete capacity and cost assumptions, and establish IaC/deployment controls before resource provisioning.

## Confidentiality

Private engineering repository. Do not redistribute architecture, diagrams, datasets, threat models, or implementation artifacts without authorization.
