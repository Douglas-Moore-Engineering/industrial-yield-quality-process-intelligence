# Project status

**Azure reference batch-inference deployment: verified.** The current GitHub demonstration scope is the private Container Apps runtime and its reproducible model results. Grafana, Azure ML-managed execution and desktop private access are deferred integrations, not acceptance requirements for this batch demonstration. Their actual status is retained below.

Status documentation reconciled 2026-09-30; execution evidence retains its original dates. Scope: **reference industrial manufacturing validation environment**. No customer plant, line, production source or pilot owner is assigned. Copper rod/wire remains illustrative.

**Lenze reference benchmark passes the fixed point-estimate thresholds locally and in Azure.** On the publisher test partition, the frozen model detects 208/320 anomalies (65% recall) with 122/1,576 false alerts (7.74% of all rows). The cutoff was set using only normal training calibration data. See [Lenze evidence](.azure/lenze-acceptance.json). This does not establish customer production readiness.

**SECOM acceptance remains incomplete.** A new frozen candidate meets the unchanged criteria on development data: 9/17 failures detected (52.94% recall), 28/317 false alerts (8.83%), with four abstentions counted in the evaluation. These are reused development rows, not fresh confirmation. The supplied Zenodo macromilling dataset predicts surface roughness from six machining inputs; it is incompatible with the frozen SECOM sensor/failure contract. Compatible independent confirmation data remains pending. See [dataset review](governance/macromilling-compatibility.md). The existing Azure baseline has not been replaced by this candidate.

Candidate: `66587bfb754049a71963a17a84300510`. It uses 20 training-selected sensors, class-balanced logistic regression and a frozen calibrated cutoff of `0.08006196823284614`. The required recall remains at least 50%, and false alerts remain at most 10% of all rows. See [model acceptance](runbooks/model-acceptance.md) and [candidate evidence](.azure/candidate-acceptance.json). That SECOM increment passed 73 tests; the subsequent Lenze increment passed 77.

## Published Azure execution evidence

Execution `job-iyqpis-dev-data-yrcuuy2` succeeded on 2026-09-29 UTC. It reproduced all 1,576 frozen decisions and 330 alerts with the expected decision hash. All 90 local tests passed. See [results report](docs/azure-validation-results.md) and [machine-readable evidence](.azure/github-validation-result.json). This is a replay of the reference benchmark, not fresh acceptance data. The evidence is published in this repository; this report does not establish fresh execution or production acceptance.

## Azure ML workspace integration requested

The private Azure ML workspace `mlw-iyqpis-dev` now exists in East US 2. Its control-plane state is Succeeded; public access is disabled, system datastores use identity, and it references new non-HNS storage `stmlncdzf5v3azstk`, existing Key Vault and Application Insights. The additive deployment preview had 14 creates and no modifications/deletions. The overall deployment succeeded; all three endpoint connections are approved, their DNS associations succeeded, and all three new DNS VNet links completed. Private-client DNS/TLS and data access are not yet tested. No compute or online endpoint was created. This is a workspace foundation, not a finished usable ML deployment: private operator access, dependency authorization, registry/model registration and a verified ML job remain pending. Compute quota requests were submitted; the ML DDSv5 request failed with QuotaNotAvailableForResource. See [quota review](governance/eastus2-quota-request.md), [integration plan](governance/azure-ml-integration-plan.md), and [portal guide](runbooks/azure-portal-guide.md). New private endpoints incur charges while retained; they do not shut down with compute.


## Grafana requested

Private Azure Managed Grafana `grafana-iyqpis-dev` deployment succeeded in East US 2. The managed AMPLS connection is approved and synchronized, inbound private DNS succeeded, and public access/API keys are disabled. The IYQPIS Reference Operations dashboard and managed-identity Azure Monitor data source were imported through a private Container Apps job, and dashboard readback passed. Grafana queries still fail Azure Monitor PrivateLinkValidationFailedError despite the approved managed endpoint and explicit hostname routing. Setup executions failed at the query check; this is not an operational monitoring pass. Temporary role removal ran after each execution. Compilation passed; preview reports eight creates and no modifications/deletions. The user instructed deployment after review of hosting and active-user charges. Both DDSv5 quota requests now failed with QuotaNotAvailableForResource. See [Grafana deployment review](governance/grafana-deployment.md).

## Monitoring completion change prepared

Two log alerts, an operations workbook, structured batch health telemetry, and seven-day blob/container recovery configuration are prepared. Both Bicep templates compile; previews show three creates and one intended blob-service modification, no deletes. The monitoring-enabled container reproduces model metrics; 90 tests pass. These changes are **not deployed or end-to-end verified**. Checkov is unavailable in the current environment; manual security review is recorded. Private log verification and live alert/restore exercises remain pending. See [completion plan](governance/monitoring-completion-plan.md) and [readiness evidence](.azure/monitoring-readiness.json).

## Recovery and monitoring assurance

Eight temporary-copy recovery cases passed: missing/corrupted frozen artifacts were refused and restored with identical predictions; source release unchanged. See [recovery evidence](.azure/lenze-recovery-evidence.json) and [runbook](runbooks/lenze-recovery.md). Read-only Azure inspection found blob soft delete disabled and no container retention/restore policy reported. Four platform Activity Log alerts are enabled; inference-job failure notification coverage remains unverified. Cloud restore, production RTO and active-service rollback are not complete.

## Additional runtime verification

Azure execution `job-iyqpis-dev-data-9ybs2wx` succeeded. All 1,576 record-level binary decisions match Windows and Linux using a canonical identifier/decision hash. This supersedes aggregate-only consistency evidence, without changing model or cutoff. Artifact-tampering and invalid-prediction checks are tested; the full suite passes 86 tests. See [consistency evidence](.azure/lenze-decision-consistency.json). Upstream extraction and physical point-in-time correctness remain unverified.

## Updated skill lifecycle review

The updated production-systems skill is now applied through a [phase-by-phase review](governance/updated-skill-gap-review.md). Training-only [feature baseline and catalog](features/README.md) have been added retrospectively without changing the model or thresholds. Upstream feature provenance, temporal correctness, production criteria and operational assurance remain unresolved. Passing the reference benchmark does not close these gates.

## Additional quality-inspection data received

Lenze-QI intake verified 5,771 matching metadata/feature records, 22 finite numeric features, and the publisher's 4,195/1,576 train/test split. All three supplied files match publisher checksums. It is a viable separate geared-motor anomaly-detection reference benchmark; training labels are all normal. The target uses explicit normal/anomalous labels; six optimized features with unverified fitting provenance are excluded. The Lenze reference model has now been fitted locally and passes both fixed point-estimate criteria on the publisher test split; Azure execution `job-iyqpis-dev-data-rptcrd5` succeeded with matching counts and checksum-verified private evidence uploads. All 77 software tests pass. The registry is private and the default data job remains manual and unchanged. See [intake review](governance/lenze-dataset-review.md).

## Milling reference build in progress

Azure authentication was verified against the approved local account context on 2026-09-28; the East US 2 platform resource group reports Succeeded. User-supplied milling data is downloaded and matches the publisher's checksum. The source has 12,363 rows across 23 distinct raw machining-setting combinations.

A deterministic, target-independent setting-group reservation assigns 6,145 rows to training, 2,359 to validation and 3,859 to testing. The reservation is in ignored `artifacts/dataset-review/milling-split-reservation.json`; the audit implementation is `src/iyqpis/milling_audit.py`. Two focused tests passed. These setting groups do not establish independent physical runs. Numeric decoding remains unresolved (43,190 input cells contain multiple periods), so no model training, acceptance claim or new Azure execution has occurred for this dataset yet. Next: resolve the source encoding, specify regression acceptance, then train and validate the milling model through the existing on-demand Azure workflow.

## Implemented and verified

- Cloud-neutral v0.6 architecture, requirements, seven event contracts and 12 design diagrams remain the baseline.
- Private Azure development platform deployed in East US 2, with managed identities, budget and operational alerts.
- On-demand data job verified across five sample datasets: 1,104,500 records, 16 artifacts, matching remote checksums, deterministic replay and unchanged blobs.
- Chronological SECOM feature/model benchmark with training-only preprocessing, later calibration, held-out metrics, numerical JSON model bundles and implementation/data lineage.
- Reference shadow guards, associative explanations, drift/calibration summaries, local review ledger, model registry/rollback, explicit-edge genealogy and historical-case retrieval.
- Software tests exercise stale/missing/invalid/domain-shift refusal, checksum failures, audit modification, duplicate dispositions, rollback and production-promotion refusal.

Azure reference AI execution and replay succeeded with the same model ID and checksum-verified evidence artifacts. No new standing service or automatic schedule was created. The **earlier SECOM baseline** still has zero held-out alert recall at its calibration-selected threshold and therefore remains blocked. The **Lenze reference model is the current passing G2 benchmark**, with 65% anomaly recall and a 7.74% false-alert burden (false alerts / all test rows) on the publisher test partition. Neither result is customer production evidence.

## Release sequence

| Gate | Current meaning |
|---|---|
| G0 data readiness | Sample pipeline passed; real-source approval absent |
| G1 reproducible baseline | Reference training and versioned evidence implemented |
| G2 offline V&V | Lenze publisher-test benchmark passes locally and in Azure; SECOM independent confirmation remains pending |
| G3 shadow | Historical reference validation only; no live plant shadow deployment |
| G4 advisory canary | Blocked: no approved pilot or site-qualified model; the passing frozen reference model is not site acceptance |
| G5 production advisory | Blocked: real acceptance, security/recovery and ownership absent |
| G6 advanced authority | Disabled; no causal/twin/safety evidence or OT write path |

## Traceability for this reference increment

| Requirements | Implementation | Evidence scope |
|---|---|---|
| FR-006/009/010/025 | operations.py process/model monitoring | Illustrative SPC/envelope checks; not full change-point detection or plant limits |
| FR-007/011/023/026 | intelligence.py training, inference, numeric contributions and manifests | Quality benchmark; no causal, yield/scrap or early-warning claim |
| FR-005/015/019/029 | Explicit-edge traversal and past-only case retrieval | Synthetic fixtures; no real material digital thread |
| FR-021/022 | Local reference review ledger | Simulated local review; enterprise authentication and realized plant outcomes absent |
| FR-024 | Verified bundle activation and rollback | Unit-tested reference registry; no production release authority |
| FR-030 | Shadow-only runtime and production gate refusal | No control connector, actuator, setpoint or safety-system writes |

## Remaining production work

Approved plant/source contracts; identifier and genealogy mapping; measured load/latency; warning horizon and feature availability; new model validation data; approved alert thresholds; data classification/retention; enterprise IAM and multi-user review service; persisted-log and paging acceptance; backup/restore and RPO/RTO; live shadow/canary trials and plant-owner approval. No production readiness or business ROI is claimed.

Existing platform follow-ups, including protected GitHub deployment activation, remain in [Azure operations](infra/azure/OPERATIONS.md). See [reference AI build and runbook](runbooks/reference-ai.md) for commands, boundaries and recovery procedures. The original pre-Azure gate documents remain historical design evidence, not the current deployment inventory.

## Updated DME assurance records

- [21-phase lifecycle and gap review](governance/updated-skill-gap-review.md)
- [Threshold verification register](governance/threshold-verification.csv)
- [Systems Engineering Management Plan](docs/systems-engineering-management-plan.md)
- [Standards applicability and assurance](governance/standards/standards_assurance_summary.md)
- [Customer/site readiness and acceptance boundary](customer/README.md)

These records are retrospective review/planning artifacts. They do not confer standards-assurance approval, ORR, CAR or production authority.
