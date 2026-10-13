# MEAS-IYQPIS-001 — Lenze anomaly recall

Record v1 · recorded 2026-10-12 (America/New_York). Retrospective documentation of existing evidence; no new execution.

## Identity and trace

| Field | Value |
|---|---|
| Measurement ID / version / recorded date | MEAS-IYQPIS-001 / v1 / 2026-10-12 |
| KPI definition / version | IYQPIS-KPI-014; [dictionary v1](../../docs/appendix-a-kpi-dictionary.md) |
| Business need | [SR-01: prevent avoidable material loss](../../requirements/traceability.csv); this benchmark tests anomaly behavior only |
| Requirements / implementation | [FR-009, FR-023, NFR-006, NFR-019](../../requirements/verification_matrix.csv); supporting evidence only, not full requirement acceptance; [src/iyqpis/lenze.py](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/blob/27367f50ef914420ca4749a48fb5b7da7652c8f4/src/iyqpis/lenze.py) |
| Acceptance criterion / protocol | [Lenze protocol v1](../lenze-protocol.json); frozen point-estimate thresholds |
| Protocol fixed date / approval state | Protocol/code write the freeze before scoring publisher test rows. The original report records a frozen protocol but no independently signed approval timestamp. This retrospective record is not a new prospective test. |
| Related / supersedes | First normalized measurement record; preserves the original evidence and decisions, supersedes no run. |

## Definition, baseline and method

| Field | Value |
|---|---|
| Definition / formula / direction | True anomaly alerts / all labeled anomalies; higher is better. |
| Unit / numerator / denominator | Labeled anomalies; numerator 208; denominator 320. |
| Baseline / evidence | No customer or pre-system operational baseline measured. Fit/calibration distributions are not realized business baselines. |
| Target / acceptance threshold / status | Protocol v1 minimum recall 0.50. Reference criterion, not customer-approved acceptance. |
| Population / inclusion / exclusions | All 1,576 publisher test records; 320 anomalies and 1,256 normal records. No test outcomes excluded. Optimized feature columns excluded because fitting provenance is unverified. |
| Independent unit / sample size / exposure | 1,576 labeled records, not a claim of 1,576 independent machines. Physical-run and variant dependence limits inferential interpretation. |
| Time window / source clock | Recorded local/Azure labeled evaluation completed 2026-09-28; source event timestamps/physical warning horizon are not qualified. |
| Comparator / split / leakage controls | Publisher train/test split; 3,343 normal training rows fit the model and 852 normal rows calibrate cutoff, grouped by hashed training variant. Test outcomes do not set the cutoff. This does not prove independent physical units or feature point-in-time validity. |
| Aggregation / uncertainty method | Point estimate only. No confidence interval retained; an independent-unit/cluster analysis is required before statistical reliability or site-generalization claims. |

## Result and scope

| Field | Value |
|---|---|
| Measurement status | measured |
| Observed result / context | 208/320 = 0.65 = 65.00%; reference point-estimate criterion passes. |
| Uncertainty estimate | Point estimate only. No confidence interval retained; an independent-unit/cluster analysis is required before statistical reliability or site-generalization claims. |
| Evaluation date / environment / data origin | Public Lenze precomputed-feature benchmark, locally evaluated and replayed in private Azure Container Apps execution `job-iyqpis-dev-data-rptcrd5`. |
| Representativeness / limitations | Weak labels; upstream extraction not reproduced. No calibrated probability, warning horizon, customer facility validation or production qualification. |
| Operational intervention / actor / time | Not applicable to this engineering/benchmark result; no customer maintenance or process intervention is evidenced. |
| Follow-up outcome / attribution | Customer outcome not measured. No avoided-loss, downtime, yield, scrap or causal-benefit attribution. |
| Financial impact basis | Not applicable; this record makes no financial-impact claim. |
| Validity / remeasurement trigger | Applies only to the bound historical artifacts. Material changes to code, model, data, configuration or operating context require a new record. |

## Evidence and reproduction

| Field | Value |
|---|---|
| Original labeled evaluation / immutable report | [.azure/lenze-acceptance.json](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/blob/27367f50ef914420ca4749a48fb5b7da7652c8f4/.azure/lenze-acceptance.json); SHA-256 `ac5c09bfe61c4df989be30abadc5b6718e91fcd8571547a4871199913e57cf7b` |
| Code binding | [src/iyqpis/lenze.py](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/blob/27367f50ef914420ca4749a48fb5b7da7652c8f4/src/iyqpis/lenze.py); SHA-256 `29f50c8098f5c7706e93731e71223dbc6661163a103d1b65af3ac2892b1c75dd` matches the evaluation freeze. The inspected commit is a later evidence snapshot; the original execution commit is not separately recorded. |
| Data snapshot / digests | `Meta_Data.csv`: `684ea6342aaea35c8ff49dc3a8cd98114caece71c181224a10ca3a47b3115634`; `Original_Features.csv`: `1a7523ba6c5c3f06f731b898ef8003d27e01d7bae1e59b19d04fc250770d60e5`. |
| Model / configuration / environment | Frozen model SHA-256 `0d8b42c52499fcabb558bcbef14ab2148050a3645c452aa6cdeb1e436a1e3165`; cutoff `0.47010843494548926`; 16 features; 500-tree IsolationForest, max_samples 256, random_state 42. Azure image `sha256:75234c6d1fe17485fb36d8d1a0918eec89bf8f6a4ee54c4c285129eb3056fe51` binds the cloud runtime; separate historical Windows dependency lock is not present in the summary. |
| Calculation / reproduction | Arithmetic: `208 / 320`. A full frozen-model replay needs the authorized source/model artifacts and [verification runbook](../../runbooks/lenze-azure-verification.md). No retraining or source-data rerun occurred in this review. |
| Evidence access / integrity review | Authorized private-repository access required. Linked report contents and SHA-256 were inspected during this documentation review. No cloud log retrieval, raw-data rerun or independent source authentication is claimed. |

## Review and acceptance

| Field | Value |
|---|---|
| Measurement owner | Dr. Douglas Moore / DME engineering lead |
| Reviewer / authority / independence | AI-assisted documentation review; no named independent reviewer or customer approver is established. |
| Criterion result | pass |
| Acceptance disposition | pending review |
| Decision reference / scope / authority | Original report `passed=true`, `production_release=BLOCKED`; [current release sequence](../../PROJECT_STATUS.md). Technical reference pass does not supply independent/customer sign-off. |
| Open conditions / owner / next action | DME lead: retain original release/runtime provenance and establish physical-unit independence, extraction validity and site-specific protocol with the actual customer owner before dependent acceptance. |
| Customer / governance handoff | [Measurement index](README.md); follow the existing status and lifecycle/customer records linked there. No new release authority. |
