# Appendix A — KPI Dictionary

Definition version 1 · 2026-10-12. Existing names and intended meanings retained; stable KPI IDs added for traceability. [Measurement index](../governance/measurements/README.md). Historical definitions remain in Git history. Reference exercise results and intended-use/customer metrics have separate records.

| KPI ID | KPI / definition | Unit / direction | Current evidence |
|---|---|---|---|
| IYQPIS-KPI-001 | First Pass Yield: Conforming output accepted without rework / total output | fraction; higher | [Not measured; MEAS-IYQPIS-PLAN-001](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-001) |
| IYQPIS-KPI-002 | Material Yield: Good material output / material input | fraction; higher | [Not measured; MEAS-IYQPIS-PLAN-002](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-002) |
| IYQPIS-KPI-003 | Scrap Rate: Scrap quantity / total processed material | fraction; lower | [Not measured; MEAS-IYQPIS-PLAN-003](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-003) |
| IYQPIS-KPI-004 | Cost of Poor Quality: Scrap + rework + hold + inspection + associated losses | currency on consistent price basis; lower | [Not measured; MEAS-IYQPIS-PLAN-004](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-004) |
| IYQPIS-KPI-005 | Warning Horizon: Time between a useful system warning and irreversible quality outcome | source-clock time; higher | [Not measured; MEAS-IYQPIS-PLAN-005](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-005) |
| IYQPIS-KPI-006 | False Alerts / Shift: Operational alert episodes adjudicated non-actionable within an eligible shift | episodes / shift; lower | [Not measured; MEAS-IYQPIS-PLAN-006](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-006) |
| IYQPIS-KPI-007 | Calibration Error: Declared difference between predicted probabilities and observed outcome rates | declared probability-error score; lower | [Not measured; MEAS-IYQPIS-PLAN-007](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-007) |
| IYQPIS-KPI-008 | Time to Trace: Elapsed time to identify upstream/downstream affected genealogy | time per event; lower | [Not measured; MEAS-IYQPIS-PLAN-008](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-008) |
| IYQPIS-KPI-009 | Time to Diagnose: Elapsed time from event recognition to accepted root-cause hypothesis | time per event; lower | [Not measured; MEAS-IYQPIS-PLAN-009](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-009) |
| IYQPIS-KPI-010 | Intervention Success: Approved recommendations followed by desired stabilized outcome / approved recommendations with evaluable follow-up | fraction; higher | [Not measured; MEAS-IYQPIS-PLAN-010](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-010) |
| IYQPIS-KPI-011 | Abstention Rate: Cases explicitly declined / eligible cases under frozen domain policy | fraction; target risk-dependent | [Not measured; MEAS-IYQPIS-PLAN-011](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-011) |
| IYQPIS-KPI-012 | Data Freshness: Age of latest acceptable source event at the declared decision boundary | time; lower | [Not measured; MEAS-IYQPIS-PLAN-012](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-012) |
| IYQPIS-KPI-013 | Genealogy Completeness: Product entities with complete required upstream lineage / eligible product entities | percent; higher | [Not measured; MEAS-IYQPIS-PLAN-013](../governance/measurements/planned-kpis.md#meas-iyqpis-plan-013) |
| IYQPIS-KPI-014 | Lenze anomaly recall: true alerts / labeled anomalies | fraction; higher | [MEAS-IYQPIS-001](../governance/measurements/MEAS-IYQPIS-001.md) |
| IYQPIS-KPI-015 | Lenze false alerts / all rows: false alerts / all publisher test rows | fraction; lower | [MEAS-IYQPIS-002](../governance/measurements/MEAS-IYQPIS-002.md) |
| IYQPIS-KPI-016 | Frozen binary decision agreement: matching binary decisions / frozen test decisions | fraction; exact equality | [MEAS-IYQPIS-003](../governance/measurements/MEAS-IYQPIS-003.md) |
| IYQPIS-KPI-017 | Sample records validated: accepted record count across the fixed sample pipeline | records; descriptive volume | [MEAS-IYQPIS-004](../governance/measurements/MEAS-IYQPIS-004.md) |

Reference metrics do not replace operational metrics. In particular, window coverage is not event recall, receipt counts are not RTO/RPO, false alerts per all test rows are not false positives per healthy row or nuisance alerts per operating hour, and processed-record counts are not realized business benefits.
