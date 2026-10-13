# Measurement and evidence index

Version 1 · 2026-10-12 · Owner: Dr. Douglas Moore. These records normalize historical evidence; they do not report new execution or change model, cloud or customer release decisions.

Business need → KPI → requirement → implementation → measurement → evidence → acceptance decision. Definitions live in the [KPI dictionary](../../docs/appendix-a-kpi-dictionary.md). [Open KPI plans](planned-kpis.md) have individual record IDs and explicit unmeasured status. [Machine-readable index](index.csv) is a navigation/status projection, not a separate acceptance authority.

| Record | Scope | Measurement / criterion / acceptance |
|---|---|---|
| [MEAS-IYQPIS-001](MEAS-IYQPIS-001.md) | IYQPIS-KPI-014 | measured / pass / pending review |
| [MEAS-IYQPIS-002](MEAS-IYQPIS-002.md) | IYQPIS-KPI-015 | measured / pass / pending review |
| [MEAS-IYQPIS-003](MEAS-IYQPIS-003.md) | IYQPIS-KPI-016 | measured / pass / pending review |
| [MEAS-IYQPIS-004](MEAS-IYQPIS-004.md) | IYQPIS-KPI-017 | inconclusive / not evaluated / pending review |

## Evidence and decision authority

Pinned links identify the exact repository evidence snapshot reviewed. A repository snapshot commit is not automatically the original executed commit; records explicitly distinguish original code/image/data digests from later documentation versions and identify provenance gaps. Historical evidence remains unchanged. Failed and inconclusive findings stay visible.

No real customer outcomes or independent sign-off are established. Each unmeasured plan has a DME owner and next action; its dependent acceptance remains open. Record corrections as new versions with rationale and retain their Git history; actual reruns receive new IDs.

Existing decisions: [Lenze evidence](../../.azure/lenze-acceptance.json), [release status](../../PROJECT_STATUS.md), [reference protocol](../lenze-protocol.json). Existing lifecycle/handoff: [lifecycle gap review](../updated-skill-gap-review.md), [customer readiness](../../customer/README.md). Reference point-estimate passes do not establish statistical or customer acceptance.

## Unquantified claims

Identity configuration, advisory authority boundaries and implemented code paths are qualitative implementation/security claims, so a numeric KPI is not applicable. Their trace remains in the existing requirements/V&V and decision registers, with implementation/evidence links from the README. Documentation of a control is not proof of its operation or acceptance.
