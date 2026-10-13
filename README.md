# Industrial Yield, Quality and Process Intelligence

**Private Azure reference deployment.** Frozen Lenze-QI benchmark inference is verified on Container Apps Jobs. Customer/site production acceptance remains **BLOCKED**. [Current release state](#qualification-gaps-and-next-work) · [Detailed status](PROJECT_STATUS.md).

## Operational problem

Manufacturing teams need to identify abnormal process or inspection behavior, investigate affected material, and decide whether intervention is justified. Industrial Yield, Quality and Process Intelligence (IYQPIS) connects data validation, anomaly evidence and an advisory engineering workflow. Copper rod/wire is the illustrative architecture scenario; the implemented passing benchmark uses Lenze geared-motor inspection features.

## Users and decisions

Quality and process engineers investigate anomalies and supporting evidence; production and maintenance owners authorize operational action. The architecture preserves existing plant controls and human authority. The reference system has no authorized path to change plant control logic, machine setpoints, interlocks or safety systems.

## What currently works

- A sample-data validation pipeline with source checksums and deterministic replay: [data engineering](runbooks/data-engineering.md).
- Frozen Lenze feature-based anomaly inference and record-level decision verification on private Azure Container Apps Jobs: [recorded Azure results](docs/azure-validation-results.md).
- Private reference infrastructure with scoped workload identities and storage/artifact access: [Azure implementation and evidence](infra/azure/README.md).
- Reference guards, an illustrative local review ledger and tested artifact rollback behavior: [implementation and boundaries](runbooks/reference-ai.md).

The [requirement verification matrix](requirements/verification_matrix.csv) distinguishes these working capabilities from planned and partially implemented functions.

## Measured results and conditions

| Metric | Recorded result / denominator | Context | Measurement record |
|---|---|---|---|
| Anomaly recall | 208 / 320 anomalies = **65.00%** | Publisher Lenze test partition; frozen point-estimate criterion at least 50% | [MEAS-IYQPIS-001](governance/measurements/MEAS-IYQPIS-001.md) |
| False alerts / all test records | 122 / 1,576 = **7.74%** | Same benchmark; criterion at most 10% of all rows; not false positives / healthy rows | [MEAS-IYQPIS-002](governance/measurements/MEAS-IYQPIS-002.md) |
| Frozen binary decision agreement | **1,576 / 1,576**, including 330 alerts | Windows, Linux Docker and Azure reference replay; no fresh test population | [MEAS-IYQPIS-003](governance/measurements/MEAS-IYQPIS-003.md) |
| Sample records validated | **1,104,500 records across five datasets**, historically reported | Data-engineering run/replay; full manifest and raw logs are outside Git and require provenance review | [MEAS-IYQPIS-004](governance/measurements/MEAS-IYQPIS-004.md) |
| Yield, scrap, diagnosis time and intervention benefit | **Not measured** | No actual customer baseline, operational intervention or follow-up outcomes | [Open measurements](governance/measurements/planned-kpis.md) |

The benchmark uses publisher-precomputed features and weak labels, which provide limited ground truth. Results describe the recorded test partition and replay; they do not establish warning time, calibrated risk or performance at other sites.

<a id="current-release-state"></a>

## Qualification gaps and next work

Lenze passes the reference model gate (G2) against its recorded point-estimate thresholds. Real plant shadow operation, site-specific validation, operational readiness, customer acceptance and production advisory authorization remain incomplete. SECOM independent confirmation remains pending. Upstream feature extraction/time availability, production service-level objectives, live notification and cloud recovery evidence remain open.

The next activity is the existing [customer/site readiness process](customer/README.md) and [operational assurance backlog](governance/reference-assurance-actions.csv). Grafana query-path and Azure ML integration limits remain in [project status](PROJECT_STATUS.md).

## Run checks or inspect the implementation

From an isolated Python environment at the repository root:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/check_repository_contract.py
```

The software checks are local. Full data/model replay requires the authorized source files and frozen artifacts described in [data engineering](runbooks/data-engineering.md) and [Lenze verification](runbooks/lenze-azure-verification.md); those bytes are not bundled here. There is no public inference endpoint or self-contained full-data demo. Inspect [source](src/iyqpis), [tests](tests), and [recorded execution evidence](docs/azure-validation-results.md) directly. Cloud execution is a separate authorized operation.

## Engineering documentation

| Review need | Authoritative entry point |
|---|---|
| Business problem and users | [Mission](docs/01-business-problem-and-mission.md), [concept of operations](docs/02-conops-and-stakeholders.md) |
| Architecture and decisions | [Architecture index](docs/architecture/README.md), [architecture decision register](architecture/architecture_decisions.csv) |
| Requirements and verification | [Requirements guide](requirements/README.md), [verification and validation matrix](requirements/verification_matrix.csv) |
| Performance indicators, measurements and decisions | [Indicator dictionary](docs/appendix-a-kpi-dictionary.md), [measurement index](governance/measurements/README.md), [release/acceptance design](docs/08-testing-release-gates-and-acceptance.md) |
| Implementation and operations | [Source](src/iyqpis), [Azure runbooks](infra/azure/README.md), [recovery](runbooks/lenze-recovery.md) |
| Lifecycle and customer handoff | [Lifecycle gap review](governance/updated-skill-gap-review.md), [customer readiness](customer/README.md), [status](PROJECT_STATUS.md) |
| Complete documentation | [Documentation index](docs/README.md), [contributing](CONTRIBUTING.md) |

Private DME engineering repository. Do not redistribute engineering material or commit credentials, customer records or unapproved dataset bytes.
