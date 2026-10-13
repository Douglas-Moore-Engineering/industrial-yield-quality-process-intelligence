# MEAS-IYQPIS-004 — Historical sample-pipeline record count

Record v1 · recorded 2026-10-12 (America/New_York). Retrospective documentation of existing evidence; no new execution.

## Identity and trace

| Field | Value |
|---|---|
| Measurement ID / version / recorded date | MEAS-IYQPIS-004 / v1 / 2026-10-12 |
| KPI definition / version | IYQPIS-KPI-017; [dictionary v1](../../docs/appendix-a-kpi-dictionary.md) |
| Business need | [SR-06: contract-based portable ingestion](../../requirements/traceability.csv) |
| Requirements / implementation | [FR-001 / FR-004 / FR-023 / NFR-016](../../requirements/verification_matrix.csv); bounded sample-pipeline evidence; [src/iyqpis/pipeline.py](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/blob/27367f50ef914420ca4749a48fb5b7da7652c8f4/src/iyqpis/pipeline.py) |
| Acceptance criterion / protocol | Historical pipeline validation, checksum readback and unchanged replay artifacts |
| Protocol fixed date / approval state | Retrospective mapping of the runbook acceptance summary. Original complete run manifest and execution logs are outside Git; their approval/version bindings are not verified in this review. |
| Related / supersedes | First normalized measurement record; preserves the original evidence and decisions, supersedes no run. |

## Definition, baseline and method

| Field | Value |
|---|---|
| Definition / formula / direction | Total accepted records across five sample datasets; volume is an engineering activity measure, not a business outcome. |
| Unit / numerator / denominator | 1,104,500 records across five datasets; not a rate or count of independent machines. |
| Baseline / evidence | No customer ingestion-time or quality baseline measured. |
| Target / acceptance threshold / status | No numeric volume performance target. Historical acceptance required valid records, checksum agreement and repeatable replay; target scope is the fixed sample run. |
| Population / inclusion / exclusions | Five datasets in run `cb03fc7d2f32c0e29031cc4fd00fc4fb`; detailed per-dataset counts, exclusions and quality outcomes require the original manifest. |
| Independent unit / sample size / exposure | Five datasets; records are not asserted independent. No production exposure or throughput duration supplied. |
| Time window / source clock | Historical live acceptance dated 2026-09-28 in the runbook. Exact start/end times are not included in its summary. |
| Comparator / split / leakage controls | Original full-data run and replay; no model train/test inference applies to this volume total. |
| Aggregation / uncertainty method | No inferential interval applicable to a deterministic count. Count has not been independently reconstructed from the original manifest in this review. |

## Result and scope

| Field | Value |
|---|---|
| Measurement status | inconclusive |
| Observed result / context | Runbook reports 1,104,500 validated records and 16 artifacts with checksum/readback replay checks. Provenance closure is incomplete in the accessible summary. |
| Uncertainty estimate | No inferential interval applicable to a deterministic count. Count has not been independently reconstructed from the original manifest in this review. |
| Evaluation date / environment / data origin | Historical local and Azure sample-data runs; no live customer telemetry. |
| Representativeness / limitations | Full source/output manifest digests, per-dataset counts, original execution/image and dependency bindings are unavailable in the committed summary. This is a documented historical count, not newly verified processing or business impact. |
| Operational intervention / actor / time | Not applicable to this engineering/benchmark result; no customer maintenance or process intervention is evidenced. |
| Follow-up outcome / attribution | Customer outcome not measured. No avoided-loss, downtime, yield, scrap or causal-benefit attribution. |
| Financial impact basis | Not applicable; this record makes no financial-impact claim. |
| Validity / remeasurement trigger | Applies only to the bound historical artifacts. Material changes to code, model, data, configuration or operating context require a new record. |

## Evidence and reproduction

| Field | Value |
|---|---|
| Immutable historical summary | [runbooks/data-engineering.md](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/blob/27367f50ef914420ca4749a48fb5b7da7652c8f4/runbooks/data-engineering.md); SHA-256 `d6ff0610c2c63ee6492754e4b5e5cc8e57f869556f4cbf37c5694aca2da977c2` |
| Supporting plan summary | [.azure/data-engineering-plan.json](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/blob/27367f50ef914420ca4749a48fb5b7da7652c8f4/.azure/data-engineering-plan.json); SHA-256 `50e92f00dc42f8f4ced2bf7d4db3f617d45ea62539ca5971a3aac1008120d3e1` |
| Run ID | `cb03fc7d2f32c0e29031cc4fd00fc4fb`; detailed logs and manifest are in the original authorized evidence store, not committed here. |
| Code / data / configuration / environment | The linked source is the inspected repository snapshot, not a verified original executed commit. Original manifest/image/dependency binding remains an explicit provenance gap. |
| Model | Not applicable: this record counts data-pipeline records. |
| Calculation / reproduction | Inspect the Acceptance and recovery section of the runbook. To close the record, obtain the authorized run manifest and recompute per-dataset totals and checksums using the existing verifier. No original raw logs or artifacts were retrieved here. |
| Evidence access / integrity review | Authorized private-repository access required. Linked report contents and SHA-256 were inspected during this documentation review. No cloud log retrieval, raw-data rerun or independent source authentication is claimed. |

## Review and acceptance

| Field | Value |
|---|---|
| Measurement owner | Dr. Douglas Moore / DME engineering lead |
| Reviewer / authority / independence | AI-assisted documentation review; no named independent reviewer or customer approver is established. |
| Criterion result | not evaluated |
| Acceptance disposition | pending review |
| Decision reference / scope / authority | Historical runbook reports acceptance; this normalization makes no new criterion determination or release approval. |
| Open conditions / owner / next action | DME lead: locate the original authorized manifest/logs, bind their hashes and executed image/code versions, reconcile all dataset totals and record a versioned correction before using this count as audit-complete evidence. |
| Customer / governance handoff | [Measurement index](README.md); follow the existing status and lifecycle/customer records linked there. No new release authority. |
