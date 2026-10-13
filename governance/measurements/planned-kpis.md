# Open KPI measurement plans

Version 1 · 2026-10-12 · Owner: Dr. Douglas Moore, DME engineering lead. These are intended-use measurement plans, not executed evaluations. Historical benchmark/service exercises do not supply missing customer observations. [Dictionary](../../docs/appendix-a-kpi-dictionary.md) · [Measurement index](README.md).

## Shared fields applying to every plan below

| Field | Current value |
|---|---|
| Measurement status / criterion result / acceptance disposition | **not measured / not evaluated / pending review** |
| Baseline / observed result / uncertainty estimate | **not measured** for the stated intended-use metric; fictional discovery assumptions are not observations |
| KPI definition version | Dictionary v1, 2026-10-12; stable IDs introduced without replacing historical requirement or decision IDs |
| Population / sample size / exposure / window | Not yet fixed for intended use; freeze coverage, independent assets/runs, timezone, missingness, exclusions and follow-up before collection |
| Method / comparator / split | Row-specific collection action below; pre-register the protocol, comparator and independent evaluation units before confirmatory testing |
| Protocol approval / reviewer / authority | No pre-evaluation approval or real customer approver is recorded; DME self-review is not independent review |
| Code / data / model / configuration / run bindings | Not applicable to an unexecuted plan; retain exact digests and environment versions when an evaluation is performed |
| Operational action / outcome / attribution | Not measured; record actor, authorized action, time, follow-up and comparator/confounders for impact claims |
| Finance basis | Monetary metrics require agreed currency/price date, net incremental costs and nonoverlapping benefit categories; otherwise not applicable |
| Validity / disposition | Proposed plans only; no acceptance/release criterion is satisfied. Create a new measurement ID for each actual evaluation |
| Handoff / next scheduling action | DME lead owns plans and must appoint the relevant customer/domain/finance owner and schedule protocol review when a real engagement supplies authorized inputs |

## MEAS-IYQPIS-PLAN-001

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-001 / v1 / 2026-10-12; IYQPIS-KPI-001: First Pass Yield |
| Need / requirements | [SR-01](../../requirements/traceability.csv); [FR-008 / FR-022](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Conforming output accepted without rework / total output; fraction; higher |
| Target / approval state | Target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Agree product/output units and comparable baseline, then capture quality dispositions, rework and interventions. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-002

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-002 / v1 / 2026-10-12; IYQPIS-KPI-002: Material Yield |
| Need / requirements | [SR-01](../../requirements/traceability.csv); [FR-008 / FR-022](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Good material output / material input; fraction; higher |
| Target / approval state | Target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Define common mass/unit basis and process boundary; reconcile inputs, good output and inventory changes. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-003

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-003 / v1 / 2026-10-12; IYQPIS-KPI-003: Scrap Rate |
| Need / requirements | [SR-01](../../requirements/traceability.csv); [FR-008 / FR-022](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Scrap quantity / total processed material; fraction; lower |
| Target / approval state | Target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Agree material basis and production window; record scrap cause, interventions and comparable baseline. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-004

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-004 / v1 / 2026-10-12; IYQPIS-KPI-004: Cost of Poor Quality |
| Need / requirements | [SR-01](../../requirements/traceability.csv); [FR-022; finance acceptance requirement not approved](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Scrap + rework + hold + inspection + associated losses; currency on consistent price basis; lower |
| Target / approval state | Target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Define nonoverlapping cost categories and price date with finance; record incremental costs and counterfactual/confounding limits. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-005

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-005 / v1 / 2026-10-12; IYQPIS-KPI-005: Warning Horizon |
| Need / requirements | [SR-01](../../requirements/traceability.csv); [FR-007 / FR-008](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Time between a useful system warning and irreversible quality outcome; source-clock time; higher |
| Target / approval state | Target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Qualify feature availability, physical outcome timestamp and actionability before temporal evaluation. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-006

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-006 / v1 / 2026-10-12; IYQPIS-KPI-006: False Alerts / Shift |
| Need / requirements | [SR-05](../../requirements/traceability.csv); [NFR-017 / FR-020](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Operational alert episodes adjudicated non-actionable within an eligible shift; episodes / shift; lower |
| Target / approval state | Target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Freeze episode grouping and shift/exposure definition; collect operator adjudication and unresolved alerts. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-007

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-007 / v1 / 2026-10-12; IYQPIS-KPI-007: Calibration Error |
| Need / requirements | [SR-05](../../requirements/traceability.csv); [FR-007 / NFR-005](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Declared difference between predicted probabilities and observed outcome rates; declared probability-error score; lower |
| Target / approval state | Scoring definition and target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Freeze calibration score, probability model, partition and independent grouping; anomaly scores alone are not calibrated risk. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-008

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-008 / v1 / 2026-10-12; IYQPIS-KPI-008: Time to Trace |
| Need / requirements | [SR-04](../../requirements/traceability.csv); [FR-005 / FR-019](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Elapsed time to identify upstream/downstream affected genealogy; time per event; lower |
| Target / approval state | Target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Define trace completeness and event start/finish; measure real genealogy investigations and comparator. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-009

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-009 / v1 / 2026-10-12; IYQPIS-KPI-009: Time to Diagnose |
| Need / requirements | [SR-02](../../requirements/traceability.csv); [FR-011 / FR-016 / FR-029](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Elapsed time from event recognition to accepted root-cause hypothesis; time per event; lower |
| Target / approval state | Target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Record analyst start, evidence review and authorized hypothesis acceptance; compare matched case complexity. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-010

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-010 / v1 / 2026-10-12; IYQPIS-KPI-010: Intervention Success |
| Need / requirements | [SR-01 / SR-02](../../requirements/traceability.csv); [FR-013 / FR-021 / FR-022](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Approved recommendations followed by desired stabilized outcome / approved recommendations with evaluable follow-up; fraction; higher |
| Target / approval state | Outcome and follow-up target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Capture authorized action, time, actor, follow-up result, exposure and comparator/confounders; report missing follow-up. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-011

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-011 / v1 / 2026-10-12; IYQPIS-KPI-011: Abstention Rate |
| Need / requirements | [SR-05](../../requirements/traceability.csv); [FR-020 / NFR-004](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Cases explicitly declined / eligible cases under frozen domain policy; fraction; target risk-dependent |
| Target / approval state | Target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Define eligibility and domain policy; report refusals separately by operating regime and outcome. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-012

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-012 / v1 / 2026-10-12; IYQPIS-KPI-012: Data Freshness |
| Need / requirements | [SR-06](../../requirements/traceability.csv); [NFR-012 / NFR-016](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Age of latest acceptable source event at the declared decision boundary; time; lower |
| Target / approval state | Target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Qualify source clock, eligible stream and decision timestamp; observe age across the actual operation window. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |

## MEAS-IYQPIS-PLAN-013

| Field | Value |
|---|---|
| Identity / KPI | MEAS-IYQPIS-PLAN-013 / v1 / 2026-10-12; IYQPIS-KPI-013: Genealogy Completeness |
| Need / requirements | [SR-04](../../requirements/traceability.csv); [FR-005 / FR-019](../../requirements/verification_matrix.csv) |
| Definition / units / direction | Product entities with complete required upstream lineage / eligible product entities; percent; higher |
| Target / approval state | Target not approved |
| Implementation / evaluation relationship | Existing source and V&V are supporting context only; no intended-use result is inferred. The linked requirements retain their own implementation/acceptance status. |
| Owner / next action | DME lead: Define required relationships and population; reconcile real source genealogy and record missing links. |
| Acceptance / decision | Pending review; see existing release/customer handoff from the measurement index. No decision is created by this plan. |
