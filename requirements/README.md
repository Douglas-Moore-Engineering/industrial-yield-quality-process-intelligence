# Requirements and verification evidence

## Contents

- [Baseline and evidence](#baseline-and-evidence)
- [Status interpretation](#status-interpretation)
- [Review and change rules](#review-and-change-rules)

## Baseline and evidence

The [functional baseline](functional_requirements.csv) and [nonfunctional baseline](nonfunctional_requirements.csv) retain all 50 original IDs and requirement statements. [Stakeholder traceability](traceability.csv) retains the six original stakeholder mappings. The [verification matrix](verification_matrix.csv) adds one assessed row per requirement; it does not replace or silently weaken the baseline.

Assessment source: commit `cc911d091323831f11f7c889a20514312d4387f8`, reviewed 2026-09-30. Author: Codex, AI-assisted repository review. Human reviewer/assurance approver: unassigned. Evidence dates remain those of the source records. This is not a fresh Azure run, independent V&V or a customer acceptance review.

Each row contains the original requirement, stakeholder need/rationale, architecture, implementation, named tests where available, recorded execution evidence, a bounded reference check, remaining acceptance work and proposed responsibility. Additional stakeholder descriptions derive from the existing ConOps; they are not new customer agreements. Semicolon-separated repository paths can use `::symbol` for Python functions/classes. Empty implementation/test/execution fields mean no matching evidence was identified for that claim. A test-file reference is evidence of test definition, not proof that it ran in this review. Historical execution reports are explicitly separate.

## Status interpretation

| Status | Count | Meaning |
|---|---:|---|
| REFERENCE_PARTIAL | 35 | Some relevant implementation exists; the complete baseline requirement is not accepted |
| REFERENCE_BOUNDARY_IMPLEMENTED | 2 | Reference authority restriction is implemented and has test definitions; site assurance remains pending |
| DESIGN_ONLY | 12 | Design/contract intent exists without sufficient executable evidence for the requirement |
| EXTENSION_PLANNED | 1 | Future extension, outside current implemented reference scope |

All 50 baseline requirements are represented. This is **100% mapping coverage**, not 100% implementation, execution coverage, conformance or acceptance. No row grants customer production authority. Several requirements combine multiple capabilities; partial support is not whole-requirement satisfaction.

The general logistic/shadow path in `intelligence.py` and `operations.py` is distinct from the Lenze IsolationForest batch path. Guardrail, probability and explanation claims must remain attached to the path actually inspected. The currently passing Lenze benchmark uses precomputed publisher features and anomaly scores, not calibrated plant risk probabilities.

## Review and change rules

1. Preserve requirement IDs, baseline statements, fixed model/protocol thresholds and original evidence.
2. Before acceptance, assign an accountable reviewer and approve measurable criteria for the relevant scope. Plant response times, SLO/RPO/RTO, throughput and business targets remain unresolved until actual needs are known.
3. Split compound requirements through controlled derived IDs and recorded impact analysis when the requirements owner approves; do not rewrite the baseline during a mapping correction.
4. On code, source, schema, feature, model, cutoff, infrastructure or authority changes, revisit affected rows and identify evidence that must be repeated.
5. Keep the [review findings](../governance/reviews/2026-09-30-reference-review.md), [assurance actions](../governance/reference-assurance-actions.csv) and [standards assurance](../governance/standards/standards_assurance_summary.md) visible. Customer-dependent closure is deferred, not waived.
