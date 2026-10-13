# MEAS-IYQPIS-003 — Frozen binary decision agreement

Record v1 · recorded 2026-10-12 (America/New_York). Retrospective documentation of existing evidence; no new execution.

## Identity and trace

| Field | Value |
|---|---|
| Measurement ID / version / recorded date | MEAS-IYQPIS-003 / v1 / 2026-10-12 |
| KPI definition / version | IYQPIS-KPI-016; [dictionary v1](../../docs/appendix-a-kpi-dictionary.md) |
| Business need | [SR-06: portability across environments](../../requirements/traceability.csv) |
| Requirements / implementation | [FR-023 / NFR-006 / NFR-015](../../requirements/verification_matrix.csv); binary replay consistency only; [src/iyqpis/lenze_verification.py](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/blob/27367f50ef914420ca4749a48fb5b7da7652c8f4/src/iyqpis/lenze_verification.py) |
| Acceptance criterion / protocol | Equality of SHA-256 over sorted `(record identifier, binary alert decision)` pairs for all 1,576 test records |
| Protocol fixed date / approval state | Verifier compares against an externally supplied frozen-manifest digest. No separate signed pre-test approval is retained; this record is retrospective. |
| Related / supersedes | First normalized measurement record; preserves the original evidence and decisions, supersedes no run. |

## Definition, baseline and method

| Field | Value |
|---|---|
| Definition / formula / direction | Matching binary decisions / all frozen test decisions; exact equality is required. Score bitwise equality is not asserted. |
| Unit / numerator / denominator | Record decisions; 1,576 / 1,576 with 330 alerts. |
| Baseline / evidence | Frozen reference digest `006803a3dab4e5c3846663428d68f13d9fa62560f00f093f8e039da086cec11c`. |
| Target / acceptance threshold / status | Exact equality to the frozen digest; engineering replay criterion, not a business-impact target. |
| Population / inclusion / exclusions | Complete publisher test partition. Verifier rejects duplicate IDs, source-set differences, invalid partitions and nonfinite input; no score-based exclusions. |
| Independent unit / sample size / exposure | One fixed dataset replayed in three runtimes. These are repeated observations of the same records, not independent predictive validation sets. |
| Time window / source clock | Original cross-runtime run `job-iyqpis-dev-data-9ybs2wx`; precise timestamp absent in that summary. Later Azure replay `job-iyqpis-dev-data-yrcuuy2`: 2026-09-29T00:29:01Z to 00:29:32Z. |
| Comparator / split / leakage controls | Same model, sources, threshold and partition as MEAS-IYQPIS-001/002. No fitting or threshold selection in the verifier. |
| Aggregation / uncertainty method | Exact finite-set hash comparison; confidence interval not applicable. Hash matching does not authenticate a release signer or prove score equality. |

## Result and scope

| Field | Value |
|---|---|
| Measurement status | measured |
| Observed result / context | 1,576/1,576 binary decisions agree across Windows Python, Linux Docker and Azure Container Apps; 330 alerts. Later Azure replay retains the same digest. |
| Uncertainty estimate | Exact finite-set hash comparison; confidence interval not applicable. Hash matching does not authenticate a release signer or prove score equality. |
| Evaluation date / environment / data origin | Reference dataset replay in Windows/Linux/Azure; no actual production events. |
| Representativeness / limitations | Only the binary decisions and bound artifacts are compared. No fresh population, upstream audio extraction or cross-site efficacy established. |
| Operational intervention / actor / time | Not applicable to this engineering/benchmark result; no customer maintenance or process intervention is evidenced. |
| Follow-up outcome / attribution | Customer outcome not measured. No avoided-loss, downtime, yield, scrap or causal-benefit attribution. |
| Financial impact basis | Not applicable; this record makes no financial-impact claim. |
| Validity / remeasurement trigger | Applies only to the bound historical artifacts. Material changes to code, model, data, configuration or operating context require a new record. |

## Evidence and reproduction

| Field | Value |
|---|---|
| Cross-runtime report | [.azure/lenze-decision-consistency.json](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/blob/27367f50ef914420ca4749a48fb5b7da7652c8f4/.azure/lenze-decision-consistency.json); SHA-256 `f34c314389dab901f426751e437c0108eaec4ba00ac930a6c7ab0fdf10880105` |
| Later Azure replay | [.azure/github-validation-result.json](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/blob/27367f50ef914420ca4749a48fb5b7da7652c8f4/.azure/github-validation-result.json); SHA-256 `685a44c3434d45a6677911dab4a3fca719a9d24a8a9157deb4c6c2cb5ee3c824` |
| Code binding | [src/iyqpis/lenze_verification.py](https://github.com/Douglas-Moore-Engineering/industrial-yield-quality-process-intelligence/blob/27367f50ef914420ca4749a48fb5b7da7652c8f4/src/iyqpis/lenze_verification.py); inspected SHA-256 `550056f03f9586e3d43fa4abc7f3cbf4c6533abaa599e93fd1acc8f27d1628b9` matches the report; original execution commit not separately retained. |
| Model / data / config | Same sources/model/cutoff as [MEAS-IYQPIS-001](MEAS-IYQPIS-001.md). Freeze SHA-256 `7963160ca9757c3c9e00383a7aedcbc247e540241ff326c3a30f11be3dbe84b6`. |
| Environment / dependencies | Three runtime classes explicitly named in the report; cloud image digest is in the labeled evaluation. Complete original host dependency locks are not included in these summary reports. |
| Calculation / reproduction | Follow [individual decision consistency](../../runbooks/lenze-azure-verification.md#individual-decision-consistency) with the original trusted frozen artifacts. Static review verified the code hash and matching report digests; no cloud job was submitted. |
| Evidence access / integrity review | Authorized private-repository access required. Linked report contents and SHA-256 were inspected during this documentation review. No cloud log retrieval, raw-data rerun or independent source authentication is claimed. |

## Review and acceptance

| Field | Value |
|---|---|
| Measurement owner | Dr. Douglas Moore / DME engineering lead |
| Reviewer / authority / independence | AI-assisted documentation review; no named independent reviewer or customer approver is established. |
| Criterion result | pass |
| Acceptance disposition | pending review |
| Decision reference / scope / authority | Recorded `per_record_decisions_match=true`; both reports retain production release BLOCKED. Human/customer acceptance remains separate. |
| Open conditions / owner / next action | DME lead: retain full runtime manifests and original execution bindings; rerun exact decision comparison after any material serving/environment change. |
| Customer / governance handoff | [Measurement index](README.md); follow the existing status and lifecycle/customer records linked there. No new release authority. |
