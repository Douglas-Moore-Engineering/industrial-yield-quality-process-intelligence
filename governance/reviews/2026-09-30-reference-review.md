# Reference engineering evidence review — 2026-09-30

## Contents

- [Basis and authority](#basis-and-authority)
- [Requirements review](#requirements-review)
- [Architecture correspondence](#architecture-correspondence)
- [Findings and disposition](#findings-and-disposition)
- [Verification and effect](#verification-and-effect)

## Basis and authority

Change record: **CR-DOC-REF-2026-09-30**. The user authorized evidence-supported repository corrections following the INCOSE chapter mapping and pre-customer review. Reviewed source: `cc911d091323831f11f7c889a20514312d4387f8`. Review performed by Codex through inspection of repository code, test definitions, design records and retained execution evidence. This is a completed **AI-assisted repository inspection**, not independent professional V&V, a signed standards assessment, stakeholder tailoring approval, ORR, CAR or production authorization. Human assurance reviewer/approver remains unassigned.

Criteria: preserve baseline IDs and frozen evidence; separate implemented behavior from design intent; attach claims to the correct runtime; disclose missing evidence; distinguish reference work from customer-dependent acceptance. The inspection does not certify all software, security or quality properties.

## Requirements review

The new [verification matrix](../../requirements/verification_matrix.csv) maps each of 30 functional and 20 nonfunctional requirements to the inspected implementation, relevant test definitions, available recorded execution evidence and remaining acceptance work. Original requirement statements and the six-row stakeholder trace remain unchanged.

Observed quality issues:

- Several requirements combine multiple capabilities. For example, FR-009 includes anomaly detection and change points; a passing anomaly benchmark does not accept the change-point capability. FR-022 requires both disposition and realized outcome; a local review ledger proves neither a real outcome nor authenticated production accountability.
- Requirements for response windows, capacity, human factors, recoverability and business value require scope-specific measures. Reference checks are stated in the matrix; unresolved plant thresholds are not fabricated.
- Need/rationale descriptions are derived from the existing mission and ConOps. They do not establish a signed stakeholder requirement or a contractual agreement.
- Every baseline requirement is mapped, but none is declared accepted for customer production. The two implemented reference-boundary rows represent restrictions in current code, not physical plant safety validation.
- Potential requirement decomposition, acceptance baselines and reviewer assignments require controlled human review (RA-01). This inspection closes missing mapping coverage, not full requirements assurance.

## Architecture correspondence

| Concern | Design record | Runtime/evidence correspondence | Assessment and remaining work |
|---|---|---|---|
| AI authority | [ConOps](../../docs/02-conops-and-stakeholders.md); ADR-001/008 | `intelligence.infer` abstains; `Ledger.activate` permits SHADOW; `production_gate` always blocks | Reference boundary corresponds; actual OT/safety interface is absent and cannot be accepted |
| Hybrid data flow | [Trade studies](../../docs/11-architecture-trade-studies.md); [context](../../docs/diagrams/01_system_context.mmd) | Sample batch pipeline and manual Container Apps job | Broad hybrid architecture is design intent; live streaming is not implemented |
| Human decisions | [HITL view](../../docs/diagrams/07_hitl_workflow.mmd) | SQLite ledger records actor/rationale and no authorized control action | Design includes future operational workflow; current ledger is local, unauthenticated and not immutable |
| Genealogy/knowledge/twin | [Digital thread](../../docs/04-data-architecture-and-digital-thread.md) | Supplied-edge traversal; no complete plant graph or validated twin | Partial traversal does not fulfill end-to-end genealogy, graph, causal or twin capabilities |
| Cloud execution | [Azure results](../../docs/azure-validation-results.md) | Frozen Container Apps batch replay, 1,576 decisions | Azure ML workspace foundation is a separate integration; do not imply AML-managed inference |
| Observation and recovery | [Operations](../../docs/07-slos-observability-and-operations.md) | Structured monitoring code; local artifact restoration; cloud monitoring changes prepared | Persisted application telemetry, paging, cloud restore and production SLO/RPO/RTO remain unverified |
| Data/feature provenance | [Feature catalog](../../features/README.md) | Frozen source/model hashes and fixed feature order | Publisher extraction formulas/units/windows and physical point-in-time validity remain unresolved |

This table records cross-view observations and unresolved differences. It is not a completed formal architecture-description conformity review; see RA-02.

## Findings and disposition

| Finding | Disposition in this change | Remaining status |
|---|---|---|
| RV-01: high-level traceability lacks individual requirement evidence | Added 50-row matrix with bounded checks, paths, tests, evidence and gaps | Mapping complete; human requirement/acceptance review open |
| RV-02: test index contains stale statements that 64/73 tests are current | Reconciled index to historical 90-test record and actual test groups | No fresh full software test run claimed |
| RV-03: one Azure summary calls 7.74% a false-alert rate without its denominator | Corrected to false alerts / all test rows; fixed protocol and results unchanged | Conventional FPR must not be substituted |
| RV-04: copper example and pre-Azure design wording can be read as current deployment state | Added explicit historical/current boundaries and current result links | Site/process suitability still unvalidated |
| RV-05: organization-controls gap lacks a concrete proposal | Added proposed practices and evidence obligations | Adoption, accountable people, competency and independent review remain open |
| RV-06: operational gaps need actionable closure evidence | Added reference assurance action register | No deployment, alert delivery, cloud restore or approvals invented |
| RV-07: chapter mapping absent from repository | Added interpretive INCOSE map with path-specific limits | No certification, grade or conformity claim added |

## Verification and effect

See [verification results](2026-09-30-verification.json) for reproducible structural checks and outcomes. Checks cover all 50 original statements, matrix path/symbol references, local Markdown links/anchors in changed documents, fixed metric arithmetic and decision-hash consistency, original evidence preservation and the scope of changed files.

The initial documentation commit `8c3fa43604d654c4dcc3d514b8cdf4dbfd47e196` changes only documentation/registers. Executable Python, tests, schemas, IaC, workflows, model protocol, feature files, original requirement baselines and historical Azure evidence are unchanged by that commit. No Azure operation or new software-test execution is represented by its structural verification report. Production gates remain blocked. Optional integrations and customer-dependent stages are not reclassified as completed.

Subsequent GitHub Actions results and the deployment-script correction are recorded separately in the [CI follow-up](2026-09-30-ci-followup.md). They do not retroactively alter the original structural verification report.

No owner, independent reviewer, customer or release authority approval is invented. The [standards obligations](../standards/standards_assurance_summary.md) and [assurance actions](../reference-assurance-actions.csv) remain authoritative about unresolved work.
