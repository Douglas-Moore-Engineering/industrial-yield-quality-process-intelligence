# Reference industrial AI build

## Scope and sequence

This is a reference industrial manufacturing validation environment. No production plant, customer line, approved production data source or plant owner is assigned. Copper rod/wire is illustrative only. The Azure development environment remains private and on demand.

| Stage | Implementation and evidence | Release meaning |
|---|---|---|
| Platform engineering | Existing East US 2 private platform, managed identities, budget and alerts | Development platform; organization-specific follow-ups remain |
| Data engineering | Five sample adapters; 1,104,500 validated records; full Azure replay and checksum verification | Complete for the sample scope |
| Feature engineering | Verified SECOM telemetry/quality join; 590 named sensors; BAD readings become missing, not zero-valued features | Sample row identifiers only; no invented lots |
| Model development | Logistic quality benchmark; train-only imputation/scaling; chronological 60/20/20 timestamp partitions | G1 reference implementation |
| Offline validation | Separate later calibration; untouched final temporal test; AP, ROC-AUC, Brier, ECE, recall and false-alert counts | Model efficacy is reported honestly; no production pass inferred |
| Shadow inference | Versioned JSON model, input/domain/freshness/envelope checks, associative explanations and evidence ID | Historical reference scoring; always ABSTAIN from plant recommendations |
| Decision workflow | Local SQLite reference ledger, mutually exclusive review dispositions, hash-chain checks | Simulated local reviewer, not enterprise authentication or immutable audit storage |
| Model operations | Verified bundle registry, shadow activation, previous-version rollback, monitoring | Rollback and tampering refusal exercised in tests |
| Trace/retrieve/monitor | Explicit-edge genealogy, past-only numeric case retrieval, three-sigma reference monitor | Synthetic fixtures; no plant genealogy or process limits claimed |
| Azure execution | Existing manual job with an execution-only AI image/template; managed-identity reads and publication | No new service, persistent compute or schedule |
| Production promotion | Always blocked in the reference implementation | G3 live shadow, G4 canary and G5 production require a real approved pilot |
| Advanced capabilities | Causal intervention, validated digital twins, prescriptive optimization and autonomy disabled | G6 safety assurance and domain evidence are absent |

The seven schema contracts and architecture diagrams remain the design basis. A benchmark does not establish warning horizon, cross-site generalization, scrap savings or causal effects. This release does not implement a multi-user operator application, real OT connectors, enterprise SSO, durable cloud review transactions or a validated process twin.

## Model evidence

The SECOM sample contains real row timestamps with an assumed UTC timezone. Equal timestamps remain within one split. Training, calibration and test periods do not overlap. Only training data determines retained sensors, medians, means and scales. Calibration fits on the middle partition; its 90th-percentile probability sets the illustrative alert threshold. The test partition is never used to fit those values. There is no claim that all source sensors were available before inspection disposition.

The initial frozen benchmark has weak alert performance: the final 317 rows contain 17 failures, but recall at the calibration-selected threshold is zero. Average precision is approximately 0.083 versus 0.054 prevalence. Its illustrative minimum-recall check therefore fails. Do not promote it because ROC-AUC or Brier looks favorable. A revised model needs a new documented experiment and fresh confirmation data; do not repeatedly tune against this exposed test set.

Each numeric JSON bundle includes feature order, preprocessing, calibration, coefficients, source manifest hash, implementation/dependency hashes, training parameters and runtime versions. The companion report and predictions are checksummed. No pickle is loaded. Hashes detect accidental/tampered content relative to a trusted manifest; they are not signatures from an independent release authority.

## Local commands

```powershell
python -m pip install -r requirements-dev.txt
$env:PYTHONPATH = 'src'
python -m iyqpis.intelligence artifacts/data-runs/<data-run-id> artifacts/model-runs
python -m iyqpis.reference artifacts/data-runs/<data-run-id> artifacts/model-runs/<model-id> artifacts/reference-validation/<new-check-id>
python -m pytest -q
```

Reference validation requires a fresh output directory. Keep its generated ledger and evidence under ignored `artifacts/`. Operator identifiers in these examples are synthetic. Never put customer names, account identifiers, tokens or source credentials into shared documentation or generated images.

## Azure operation

Build `infra/data/Dockerfile.ai`. It includes only source, schemas and pinned direct requirements, runs as UID 10001 and uses one numerical-library thread. Sample data and local Azure context are excluded from the image. Publish with the already-reviewed registry procedure in [data engineering](data-engineering.md), using a separate ignored `ai-job.parameters.local.json` copy so the default data image remains unchanged.

```powershell
./infra/azure/Invoke-ReferenceAI.ps1 -ApproveRun
./infra/azure/Invoke-DataJob.ps1 -Action Status
```

The launcher checks company context, region, manual trigger, timeout/retry bounds, inactive job state, private registry and immutable image digest. It submits a complete execution override, preserving the default data job. The AI run reads the completed data manifest, downloads and verifies its declared artifacts, trains the reference model, exercises the reference workflow, and uploads checksum-verified evidence to `curated-evidence/models/<model-id>/`. Consumers must wait for `release.json`, written last. `manifest.json` covers the model bundle; `release.json` additionally covers the reference validation report. The cloud check uses an ephemeral simulated review ledger and publishes its report, not a durable human-review database.

The existing 2-vCPU/4-GiB Consumption limits apply: one-hour attempt timeout and one retry. Each manual run incurs compute/storage/log costs under the previously reviewed estimate. No schedule or always-on inference endpoint is created. Existing platform service charges continue while job compute is idle.

### Verified Azure acceptance — 2026-09-28

The reference AI execution and replay both succeeded. They produced the same model ID, `67719cb11eb996943eb393ecec7a3740`, from the verified cloud data run. Five model/reference artifacts plus the final release marker were published with remote checksum verification; replay verified existing artifacts without overwrite. Stale and unknown-domain examples abstained. The benchmark's held-out average precision was 0.0830 and recall at its selected threshold was 0.0, so the model remains blocked from production acceptance.

The software suite passed 64 tests. The Linux non-root container completed isolated training/reference checks. Operator guard tests passed for approval, complete execution overrides, concurrent-run refusal and private-registry requirements. The registry publishing window was closed and verified. See [sanitized release evidence](../.azure/reference-ai-evidence.json); detailed Azure execution responses are in ignored local files. No customer information, account identifiers or credentials are included in shared evidence.

## Incident and recovery steps

| Trigger | Response |
|---|---|
| Missing, stale, future-dated or unknown-domain input | Abstain; inspect source timestamps, quality flags and mapping; do not relax limits to force a score |
| Input/model checksum mismatch | Reject the run or activation; inspect trusted source and manifests; do not overwrite evidence |
| Drift, calibration degradation or excessive false alerts | Keep shadow-only; examine matched outcomes, source changes and retained feature distribution; open a new offline experiment |
| Failed Azure execution | Inspect execution status and console logs; no completion marker means uncommitted output; retry the same immutable image/data after correction |
| Model rollback | Re-verify the previous registered bundle, then activate it in SHADOW; tests prove the previous model ID is restored |
| Duplicate or conflicting review | Reject the second decision; preserve the first and investigate using the audit sequence |
| Audit mismatch | Stop treating the local ledger as trustworthy; preserve it for investigation and recover from an independently retained copy |
| OT connectivity interruption | No OT connection exists in this reference build; real store-and-forward recovery remains a pilot acceptance requirement |
| Restore, performance or log-delivery acceptance | Run and record real target-specific tests before production; current unit and sample tests are not substitutes |

## Sources

- [SECOM dataset provenance](https://archive.ics.uci.edu/dataset/179/secom)
- [Scikit-learn data-leakage guidance](https://scikit-learn.org/1.8/common_pitfalls.html)
- [Azure manual job execution templates](https://learn.microsoft.com/en-us/azure/container-apps/jobs)
