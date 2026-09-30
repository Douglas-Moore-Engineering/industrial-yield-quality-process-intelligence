# Proposed organization controls for reference engineering

Status: **draft for DME owner review; not an adopted organization policy or completed assurance approval**. Prepared 2026-09-30 by Codex during the authorized repository correction. Accountable organization owner and reviewer assignments must be recorded by DME. Proposed roles below do not establish appointment, competence or independence.

## Contents

- [Proportionate responsibilities](#proportionate-responsibilities)
- [Proposed controls and evidence](#proposed-controls-and-evidence)
- [Review and adoption](#review-and-adoption)

## Proportionate responsibilities

A single-person business can hold multiple responsibilities. Record who actually performs each task, disclose combined roles, and obtain independent review where the consequence of failure requires it. GitHub access or CODEOWNERS routing establishes neither technical competence nor approval of an assurance claim. An AI-assisted inspection is not an independent professional assessment.

## Proposed controls and evidence

| Control | Proposed practice | Existing project evidence | Evidence still required |
|---|---|---|---|
| Configuration/change | Identify changed requirements, artifacts, evidence, rollback compatibility and release authority before promotion | Git history; frozen manifests; [SEMP](../docs/systems-engineering-management-plan.md); [verification matrix](../requirements/verification_matrix.csv) | Named owner, reviewed change disposition and evidence of use |
| Competence | Match each engineering responsibility to demonstrated training/experience; identify specialist support and review limits | [ConOps role list](../docs/02-conops-and-stakeholders.md) | Role-to-person competency assessment and development/review records; no qualifications inferred from files |
| Suppliers/data rights | Record supplier/source, version, license, permitted use, integrity and restrictions before use or transfer | [Sample sources](../data/samples/README.md); [Lenze intake](lenze-dataset-review.md) | Approved source/license inventory, dependency/supplier review and applicable contract restrictions |
| Information/retention | Classify information; define access, retention, backup, disposal and ownership by artifact class | Private repository; source hashes; [customer boundary](../customer/README.md) | Adopted retention schedule, accountable owner and tested enforcement; do not invent a legal retention period |
| Reusable IP | Separate reusable background code, publisher assets and future customer-derived artifacts | [Customer ownership boundary](../customer/README.md) | Approved IP/license inventory and engagement-specific agreement before transfer |
| Incident/learning | Preserve symptoms, versions and evidence; investigate causes; review corrective-action effectiveness | [Recovery runbook](../runbooks/lenze-recovery.md) | Actual incident or exercise records, escalation ownership and effectiveness checks |
| Professional judgment | Record assumptions, limitations, dissent, conflicts and uncertainty; keep claims within observed evidence | Reference scope and blocked production in [status](../PROJECT_STATUS.md) | Human review minutes and disposition of material concerns |
| Inclusive participation | Plan accessible review methods and obtain input from affected roles and intended users | Stakeholder concerns in ConOps | Actual participation, accessibility evaluation and response to feedback; no completed study claimed |

## Review and adoption

The DME owner should record adopted controls, responsible people, effective date, review cadence and any justified exceptions. Reviewers should record competence relevant to the assignment and whether their review is independent of implementation. Reference-only evidence may be reviewed before a customer exists; operational commitments, customer approvals and intended-user acceptance remain engagement-specific.

Track these actions in [RA-07 and RA-09](reference-assurance-actions.csv). Drafting this document closes only the absence of a concrete proposal. It does not close the organization-controls assurance obligation.
