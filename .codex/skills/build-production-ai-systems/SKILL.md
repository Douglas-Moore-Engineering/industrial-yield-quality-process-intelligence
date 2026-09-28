# Build Production AI Systems

## Purpose

Build production-grade enterprise AI systems using Douglas Moore Engineering (DME) standards for systems engineering, architecture, data, AI/ML, security, governance, observability, deployment readiness, and evidence-based release decisions.

Use this skill for substantial AI systems work, including new system design, architecture reviews, productionization, repository creation, documentation packages, cloud-readiness gates, and implementation planning.

The governing standard is **Principal Architect production structure**. The repository and documentation must read like an engineered system, not a collection of notebooks, loose diagrams, or disconnected files.

---

## 1. Mandatory operating principles

1. Start from the business/mission problem, stakeholders, operating context, measurable outcomes, constraints, assumptions, risks, and acceptance criteria.
2. Do not select cloud products before cloud-agnostic requirements, trust boundaries, SLOs, capacity assumptions, data contracts, threat model, release gates, and architecture trade studies are established.
3. Preserve validated core logic when evolving an existing system.
4. Distinguish:
   - source observations,
   - derived features,
   - model inference,
   - recommendations,
   - human decisions,
   - realized outcomes.
5. Do not fabricate business outcomes, model performance, production scale, ROI, or cloud sizing.
6. Human operational authority remains explicit unless a separately validated bounded-autonomy safety case exists.
7. Every consequential architectural decision must be traceable to a requirement, constraint, risk, SLO, cost, security need, or operational outcome.
8. Use reliable external references when architecture conventions, industrial/security requirements, standards, or technical claims need verification.
9. Use available plugins/connectors when they materially improve the work. Do not ignore connected diagram, GitHub, cloud, document, or other relevant tools.
10. Apply lifecycle phases by system applicability. Mandatory sequencing governs all applicable phases, but a phase may be marked **Not Applicable** when the system does not require that capability. Record the rationale, owner/approver, and downstream impact; never silently omit a phase or force an unnecessary technology into a system.

## 1.1 Authoritative lifecycle execution order

The numbered sections in this skill and the control numbers in the 50-control assurance framework are a **control taxonomy**, not a literal implementation sequence.

For production builds, use this execution order unless a documented architecture decision justifies a deviation:

1. **Business & systems engineering definition** — establish mission, stakeholders, operating concept, scope, measurable outcomes, constraints, assumptions, risks, acceptance criteria, and authority boundaries.
2. **Systems architecture & technical management** — establish requirements traceability, system context, interfaces, data contracts, trust boundaries, SLO categories, capacity variables, architecture trade studies, ADRs, threat model, and cloud-entry gates.
3. **Cloud foundation / landing-zone architecture** — map the cloud-agnostic architecture to tenant/account hierarchy, management groups/OUs, subscriptions/accounts, regions, network topology, DNS, identity, governance, and shared-service boundaries without premature SKU commitment.
4. **Platform Engineering & DevSecOps foundation** — implement the reusable engineering platform before workload-specific data and ML implementation. This includes IaC, CI/CD, environment separation, workspace/developer-experience standard, identity patterns, secrets, registries, policy-as-code, baseline observability, artifact promotion, supply-chain controls, and reusable golden paths.
5. **Security, privacy, and observability implementation baseline** — implement the controls required by the threat model and data classifications as part of the platform/workload foundation. Security and observability are cross-cutting; they are not deferred until the end.
6. **Data & streaming engineering** — onboard governed data, validate contracts, implement raw/validated/contextualized/curated zones as applicable, lineage, quality controls, streaming/batch paths, retention, and digital-thread/data-product services.
7. **Process and data baseline engineering** — establish the measured reference state from governed source/contextualized data before serious feature or model optimization. Characterize normal process behavior, outcome/base rates, variation, capability, seasonality/shift/site effects, equipment/material context, data-quality behavior, event rate, payload/burst behavior, latency/warning horizon, and alert burden.
8. **Process and data threshold engineering** — derive and validate thresholds that are meaningful at the source/process layer, including SPC/control limits, process operating envelopes, data-quality limits, source freshness/staleness thresholds, warning-horizon targets, capacity/scaling triggers, and pilot acceptance criteria. Do not create feature- or model-derived thresholds before those artifacts exist.
9. **Feature engineering** — define, compute, validate, and version model-ready features from governed source data and the approved process/data baseline. Enforce temporal causality/point-in-time correctness, prevent leakage, preserve feature provenance, document transformations/units/windows, test feature quality, and establish reusable feature definitions before model training.
10. **Feature baseline & validation** — after features are engineered, establish and version each production feature's reference distribution, expected range, missingness/freshness behavior, segment behavior, stability characteristics, correlation structure where relevant, and drift/domain-shift reference. Validate point-in-time correctness and training-set reproducibility before the feature is promoted for model use.
11. **Feature store / feature management** — govern reusable features across training and inference. Maintain a feature catalog/registry, ownership, lineage, versioning, freshness, offline/online consistency, access controls, point-in-time retrieval, deprecation policy, and training-serving-skew checks. A dedicated managed feature-store product is conditional; the governed feature-management capability is required only when reuse/serving requirements justify it.
12. **ML / MLOps / AI engineering** — implement training/evaluation, registries, model/agent services, inference, human-in-the-loop controls, evidence manifests, drift/calibration checks, and deterministic rollback on top of the established platform, approved process/data baseline and thresholds, and governed feature layer. Model-specific anomaly, classification, calibration, abstention, and decision thresholds are derived here from validation evidence; they are not part of the earlier process baseline.
13. **Application / decision-intelligence integration** — implement APIs, user workflows, policy/authorization gates, recommendation/evidence surfaces, business-process integration, and alert/severity policies. Alert escalation and action thresholds are validated here against operational burden and human factors.
14. **Security, privacy, and observability assurance** — verify that the previously implemented security/privacy/observability controls operate as designed through access tests, threat-control validation, vulnerability/supply-chain checks, audit-log verification, monitoring tests, and compliance evidence collection.
15. **Reliability, V&V, and operational assurance** — validate SLOs, failure modes, degraded behavior, capacity, load, backup/restore, RPO/RTO, DR, rollback, incident response, runbooks, and production-operability evidence.
16. **Production release and continuous operation** — promote only after evidence-based release gates pass; then monitor outcomes, drift, reliability, cost, security posture, baseline validity, threshold effectiveness, and control effectiveness continuously.


## 1.3 Thresholds as verification and release criteria

Thresholds are not documentation-only targets. Once a baseline is established, applicable thresholds become explicit verification and release criteria. Engineering must continue against those criteria until they are satisfied with evidence, or the system remains gated.

Required operating loop:

```text
Measure baseline
      ↓
Derive evidence-based threshold / acceptance criterion
      ↓
Engineer or configure the system
      ↓
Verify against the threshold
      ↓
PASS → advance to the next gate
FAIL → root-cause analysis → remediate → retest
      ↓
If unresolved → approved exception, reduced scope, degraded/abstain mode, or NO-GO
```

Rules:

- do not weaken or move a threshold merely to obtain a passing result,
- thresholds must be traceable to a requirement, risk, SLO, stakeholder acceptance criterion, operating constraint, or measured baseline,
- thresholds must state directionality and comparison semantics, such as `>=`, `<=`, `=`, range, or zero-tolerance,
- verification evidence must identify the dataset/environment/version, test method, measured value, threshold, result, owner/reviewer, and release gate,
- a failed critical threshold blocks promotion unless an explicitly approved exception or reduced operating scope is documented,
- provisional thresholds must be labeled provisional and cannot support an unqualified production GO,
- threshold changes require rationale, versioning, approval, and impact review; historical results must remain reproducible against the threshold version in force at the time,
- production monitoring must detect when previously satisfied thresholds are later violated and route the system into the defined response, rollback, degraded, abstain, or incident workflow.

Examples of threshold directionality:

- data completeness `>=` minimum,
- missingness `<=` maximum,
- warning horizon `>=` required minimum,
- false-alert burden `<=` approved maximum,
- latency `<=` maximum,
- availability `>=` SLO,
- calibration error `<=` tolerance,
- recovery time `<=` RTO,
- unauthorized control-path writes `= 0`,
- cost/unit `<=` approved budget threshold.

Apply this verification-driven loop at every relevant lifecycle layer: data, process, features, models, application/decision intelligence, platform, security, reliability, and business/operational acceptance.

### 1.2 Control-order mapping

When using the 50-control framework, execute the major domains operationally as:

`Controls 1–20 → Controls 36–42 → Controls 21–27 → Controls 28–35 → Controls 43–46 → Controls 47–50`

Interpretation:

- **Controls 1–20** define the business/system architecture and cloud foundation.
- **Controls 36–42** establish Platform Engineering & DevSecOps before workload engineering.
- **Controls 21–27** implement Data & Streaming Engineering on the governed platform.
- **Process/Data Baseline and Process/Data Threshold Engineering** are execution gates between Controls 21–27 and feature/model work. They establish the measured source/process reference state and only the thresholds that can be defensibly derived at that layer.
- **Feature Engineering → Feature Baseline & Validation → Feature Store / Feature Management (when applicable)** occur before model development. Feature reference distributions and feature-drift baselines are created only after the features exist.
- **Controls 28–35** implement ML/MLOps/AI capabilities on governed data, platform services, approved baseline/threshold evidence, and the governed feature layer.
- **Controls 43–46** are the formal security/privacy/observability assurance stage, while their requirements and baseline controls are designed and implemented earlier.
- **Controls 47–50** are the formal reliability/assurance/operations stage, while reliability requirements such as SLOs, RPO/RTO, degraded mode, capacity, and rollback are defined earlier.

Do not build data pipelines, model infrastructure, or production AI services first and then retrofit Platform Engineering, security, observability, or reliability controls afterward.

---

# 2. DME Repository Standard

## 2.1 Repository is an engineering deliverable

Do not create a file dump.

The repository must function as the authoritative engineering workspace and present the system coherently to an architect, engineer, client, reviewer, or technical hiring panel.

The root `README.md` is the executive entry point.

It must include:

- system title,
- concise mission,
- current architecture/release gate,
- table of contents,
- problem statement,
- architecture thesis,
- authority/safety boundary,
- architecture overview,
- engineering-documentation index,
- requirements/governance index,
- diagram index,
- repository structure,
- current evidence/release state,
- next phase,
- confidentiality / data-handling note when applicable.

## 2.2 Required repository structure

Adapt names when domain-specific, but preserve the structure and purpose.

```text
.
├── README.md
├── PROJECT_STATUS.md
├── SECURITY.md
├── CONTRIBUTING.md
├── CODEOWNERS
├── .gitignore
├── .env.example
├── <project>.code-workspace
├── .vscode/
│   ├── extensions.json
│   ├── settings.json
│   └── tasks.json
│
├── docs/
│   ├── README.md
│   ├── 01-business-problem-and-mission.md
│   ├── 02-conops-and-stakeholders.md
│   ├── 03-requirements-and-traceability.md
│   ├── 04-data-architecture-and-digital-thread.md
│   ├── 05-ai-ml-and-decision-intelligence.md
│   ├── 06-security-and-threat-model.md
│   ├── 07-slos-observability-and-operations.md
│   ├── 08-testing-release-gates-and-acceptance.md
│   ├── 09-cloud-entry-gate.md
│   ├── 10-capacity-and-performance-planning.md
│   ├── 11-architecture-trade-studies.md
│   ├── 12-architecture-decisions.md
│   ├── 13-runbooks-and-backlog.md
│   ├── appendix-a-kpi-dictionary.md
│   ├── appendix-b-assumptions-register.md
│   ├── appendix-c-reference-set.md
│   │
│   ├── architecture/
│   │   └── README.md
│   │
│   └── diagrams/
│       ├── 01_system_context.mmd
│       ├── 02_conops.mmd
│       └── ...
│
├── requirements/
│   ├── functional_requirements.csv
│   ├── nonfunctional_requirements.csv
│   └── traceability.csv
│
├── architecture/
│   ├── architecture_decisions.csv
│   └── adr/
│
├── governance/
│   ├── release_gates.md
│   └── cloud_entry_criteria.csv
│
├── data/
│   ├── contracts/
│   ├── samples/
│   └── lineage/
│
├── features/
│   ├── feature_definitions/
│   ├── feature_catalog.yaml
│   ├── feature_lineage.csv
│   └── feature_store_design.md
│
├── src/
├── tests/
├── notebooks/
├── runbooks/
├── config/
├── outputs/
│
└── infra/
    ├── azure/
    ├── aws/
    └── modules/
```

Only include cloud directories relevant to the project.

## 2.3 README table of contents

The root README and the main documentation index must contain linked tables of contents.

The README should not require the reader to hunt through folders to understand:

- what the system does,
- why it exists,
- how it is architected,
- what is implemented,
- what is not implemented,
- what evidence exists,
- what remains blocked.

## 2.4 Documentation hierarchy

The repository should mirror the architecture package.

Do not bury the full system architecture only inside a Word or PDF attachment.

Convert key sections into GitHub-readable Markdown and preserve machine-readable registers such as:

- requirements,
- traceability,
- ADRs,
- threat register,
- KPI dictionary,
- assumptions,
- cloud-entry gates,
- release gates.

Binary documents may be included as client/presentation baselines, but they are not a substitute for browsable repository documentation.

## 2.5 GitHub diagram requirement

All architecture diagrams must be in the repository.

Each diagram must have:

1. editable source under `docs/diagrams/`,
2. a human-readable title,
3. a short architectural purpose,
4. GitHub-rendered representation in `docs/architecture/README.md`,
5. links from the root README diagram index.

Do not make reviewers download a DOCX/PDF simply to see the system architecture.

---

# 3. DME Diagram Standard

## 3.1 Page standard

For client/document deliverables:

- page size: **8.5 × 11 inches**
- orientation: **portrait**
- white background
- one coherent architectural purpose per page
- use nearly the full printable area
- text must be readable at normal document zoom
- do not shrink diagrams to fit excessive content
- split dense diagrams into additional views instead

## 3.2 Visual language

Use a restrained professional enterprise palette.

Color distinguishes meaning, such as:

- actors / people,
- plant / OT,
- data,
- AI / analytics,
- policy / governance,
- security,
- authorized operations,
- evidence / audit.

Do not use decorative backgrounds that compete with the architecture.

Use consistent visual semantics across all diagrams in a project.

## 3.3 Swim lanes

Use swim lanes whenever responsibility, ownership, trust zone, lifecycle stage, or operational domain matters.

Swim lanes must be:

- visually consistent,
- aligned,
- clearly titled,
- structurally stable across related diagrams.

Typical lanes include:

- Plant / OT,
- Industrial DMZ,
- Industrial Data Platform,
- AI / Analytics,
- Policy / Governance,
- Operator / Engineer,
- Authorized Operations,
- Security / Observability,
- Data Engineering,
- Model Engineering,
- Release Authority.

Do not arbitrarily change lane style between diagrams.

## 3.4 Connectors

For workflow diagrams:

- use **curved/spline connectors** by default,
- route long feedback loops around the primary forward flow,
- minimize crossings,
- keep labels readable,
- avoid right-angle routing unless topology clarity specifically benefits from it.

For deployment/topology diagrams, orthogonal connectors may be used when they improve structural clarity.

## 3.5 Decisions, merges, forks, and joins

Notation must represent real execution semantics.

### Decision / branch
Use a diamond.

### Exclusive merge
Use a diamond when mutually exclusive branches converge.

Example:

`Approve OR Modify → exclusive merge → authorized execution`

### Parallel fork
Use only when multiple branches actually execute concurrently.

### Parallel join
Use only when all concurrent branches must complete before downstream execution.

### Prohibition
Do **not** use black synchronization bars or join bars for mutually exclusive branches such as:

- Approve,
- Modify,
- Reject.

Those are not parallel activities.

## 3.6 Human-in-the-loop semantics

For advisory industrial/enterprise AI systems, show the authority chain explicitly:

```text
AI evidence/recommendation
        ↓
Policy / guardrail validation
        ↓
Authorized human review
        ↓
Approve / Modify / Reject
        ↓
Existing authorized work/control
        ↓
Outcome verification
        ↓
Decision / outcome ledger
        ↓
Learning feedback
```

The AI path must not visually imply direct control authority unless the system has a separately documented and approved bounded-autonomy safety case.

## 3.7 Mermaid and diagram plugins

Use available diagram plugins for workflow validation.

Preferred approach:

- **Mermaid** for GitHub-rendered workflows, swim-lane-like grouped flows, lifecycle diagrams, sequences, and documentation diagrams.
- **Graphviz** only when it provides materially better topology control or rendering precision.
- Use other available design/diagram plugins when they materially improve quality.

Always inspect rendered output.

Do not assume valid syntax equals a good diagram.

Check:

- legibility,
- lane consistency,
- line crossings,
- connector semantics,
- text size,
- page utilization,
- visual balance,
- gateway correctness.

## 3.8 Minimum diagram set for substantial enterprise AI systems

Use only diagrams that add architectural value, but substantial systems should generally include:

1. System Context and Authority Boundaries
2. Concept of Operations
3. Functional Capability Decomposition
4. Data Architecture / Digital Thread / Lineage
5. Integration Architecture
6. Security / Trust Zones
7. MLOps / Model Lifecycle
8. Human-in-the-Loop Decision Workflow
9. Threat Model / Defense in Depth
10. Requirements Traceability / Verification Chain
11. Release Pipeline / Promotion Gates
12. SLO / Observability / Operational Response
13. Deployment Topology
14. Sequence diagram for a critical runtime path when useful

---

# 4. Systems Engineering Baseline

Before implementation, establish:

- business problem,
- system mission,
- stakeholders,
- RACI / decision authority,
- CONOPS,
- operational scenarios,
- scope,
- explicit out-of-scope,
- assumptions,
- constraints,
- functional requirements,
- non-functional requirements,
- acceptance criteria,
- KPIs,
- risks,
- threat model,
- system boundaries,
- trust boundaries,
- data domains,
- interfaces,
- SLOs,
- verification strategy,
- release gates,
- rollback strategy,
- runbook requirements.

Use stable IDs such as:

- `FR-001`
- `NFR-001`
- `SR-001`
- `AC-001`
- `ADR-001`
- `T-001`
- `SLO-001`

---

# 5. Requirements Traceability

Maintain a traceability chain:

```text
Business / mission need
        ↓
Stakeholder requirement
        ↓
System requirement
        ↓
Architecture component
        ↓
Implementation / configuration
        ↓
Verification method
        ↓
Evidence / KPI
        ↓
Release gate
```

Do not call architecture production-ready if key requirements lack verification evidence.

---

# 6. Data Architecture Standard

Define:

- canonical domains,
- schemas,
- identifiers,
- timestamps,
- engineering units,
- data-quality flags,
- provenance,
- lineage,
- retention,
- data classification,
- source-of-truth rules.

Preferred logical pattern:

```text
Raw / immutable
    ↓
Validated
    ↓
Contextualized
    ↓
Feature / model-ready
    ↓
Curated analytics
    ↓
Evidence / audit
```

Separate source observations from model inference.

For physical/industrial systems, treat genealogy and digital thread as first-class architecture, not an optional analytics layer.

---

# 6.1 Process / Data Baseline & Threshold Engineering

This is a **formal lifecycle gate after Data Engineering and before Feature Engineering**.

Do not begin serious predictive-model optimization until the system has an evidence-backed reference of normal/acceptable operating behavior and explicitly governed thresholds.

Establish, where relevant:

- population and outcome/base rates,
- central tendency, spread, quantiles, and distribution shape,
- process capability and stable operating envelopes,
- shift, line, site, product, recipe, material-lot, equipment-state, and seasonal effects,
- missingness, duplication, staleness, timestamp integrity, unit consistency, and other data-quality behavior,
- normal event rate, payload size, burst behavior, retention demand, and latency/warning-horizon characteristics,
- normal alert frequency and false-alert burden,
- class imbalance and decision-cost context,
- known-good and known-bad operating windows where evidence permits.

Derive thresholds from measured evidence and documented operating requirements. Examples include:

- SPC/control limits,
- process-capability limits,
- data-quality thresholds,
- source/process anomaly or change thresholds only where they are defined directly from non-model process evidence,
- warning-horizon targets,
- pilot acceptance thresholds,
- capacity and scaling trigger thresholds.

Do **not** invent thresholds merely to make a system runnable. Thresholds established in this phase become verification criteria for downstream engineering and release gates; the objective is to satisfy them with evidence, not merely record them. When evidence is insufficient, record the threshold as provisional, document the assumption/rationale, and gate production use until representative data or stakeholder approval resolves it.

Do **not** place thresholds in this phase that depend on engineered features or trained models. Feature reference distributions belong to Feature Baseline & Validation. Model score, calibrated risk, classification, abstention, and model-drift thresholds belong to ML/MLOps validation. Alert severity/action thresholds belong to Application / Decision-Intelligence integration.


Required baseline/threshold evidence should include, as applicable:

```text
baseline_profile.json
process_control_limits.csv
source_reference_distributions/
data_quality_thresholds.yaml
capacity_thresholds.yaml
acceptance_thresholds.md
baseline_evidence_report.md
```

Equivalent names/formats are acceptable if the repository preserves:

- source dataset/version and provenance,
- analysis window and inclusion/exclusion rules,
- population/segment definitions,
- calculation method,
- threshold rationale,
- owner/approver,
- effective version/date,
- validation results,
- recalibration/review trigger,
- traceability to requirement/KPI/release gate.

The baseline is versioned evidence, not a one-time notebook result. Re-establish or recalibrate it when material process, equipment, data-source, product, environment, or operating-regime changes occur.

---

# 6.2 Feature Engineering

Feature Engineering is a **formal lifecycle phase after Process/Data Baseline & Threshold Engineering and before model training**.

Define features from governed source observations and approved baseline context. Every production feature must be reproducible, traceable, temporally valid, and testable.

Required practices include, as applicable:

- explicit feature name, description, owner, source fields, units, grain, and business/physical meaning,
- deterministic transformation logic and versioning,
- point-in-time correctness and temporal causality,
- leakage prevention, especially for quality outcomes, future maintenance, labels, and post-event information,
- lag, rolling-window, rate-of-change, trend, stability, and process-window features,
- material-lot, recipe, line, site, equipment-state, maintenance-state, and genealogy-derived context where justified,
- missingness/imputation rules that do not hide source-quality failure,
- outlier and invalid-domain handling,
- feature quality tests, distribution checks, and expected ranges,
- reproducible training-set assembly,
- feature lineage back to canonical source contracts,
- documented deprecation/replacement rules.

Do not perform arbitrary feature transformation solely to improve a score. Features must remain defensible against the system requirements, physical/process meaning, temporal validity, and operational use.

Required feature-engineering evidence should include, as applicable:

```text
features/
├── feature_catalog.yaml
├── feature_definitions/
├── feature_lineage.csv
├── feature_quality_rules.yaml
├── feature_tests/
├── point_in_time_validation.md
├── leakage_assessment.md
└── training_dataset_manifest.json
```

A feature is not production-ready because it exists in a notebook. It must have an owned definition, reproducible implementation, validation evidence, lineage, and a governed lifecycle.

---

# 6.3 Feature Baseline & Validation

After Feature Engineering and before model training, establish a governed reference baseline for production features. A feature baseline cannot be created before the feature definition and computation logic exist.

Required practices include, as applicable:

- reference distribution and quantiles by relevant population/segment,
- expected range/domain and invalid-value rules,
- missingness and freshness behavior,
- stability and seasonality characteristics,
- feature correlation/dependency structure where operationally meaningful,
- point-in-time validation evidence,
- training-set reproducibility and snapshot/version manifest,
- drift/domain-shift reference statistics,
- segment-specific baselines when one global distribution would hide material differences,
- baseline version/effective date and recalibration triggers.

Required evidence should include, as applicable:

```text
features/
├── feature_reference_distributions/
├── feature_baseline_manifest.json
├── feature_validation_report.md
├── feature_drift_reference.yaml
├── segment_baselines/
└── baseline_recalibration_policy.md
```

Do not derive model decision thresholds in this phase. This phase establishes feature behavior and validity; model-score and decision thresholds are created after model validation/calibration.

---

# 6.4 Feature Store / Feature Management

Feature Store / Feature Management is the governed capability for **discovering, versioning, reusing, materializing, serving, and monitoring features across training and inference**.

The capability is required when features are reused across models, teams, batch/online paths, or production inference. A dedicated managed feature-store product is **conditional**; do not add one unless workload requirements justify its operational cost and complexity.

The feature-management design must address, where relevant:

- feature catalog and discoverability,
- feature ownership and approval,
- source and transformation lineage,
- feature/version immutability and compatibility,
- offline historical materialization for training,
- point-in-time correct retrieval,
- online/low-latency serving only when required,
- freshness and staleness SLOs,
- access control and data-classification inheritance,
- training-serving consistency,
- skew detection,
- backfill/recompute policy,
- cache/TTL semantics where applicable,
- retention, deprecation, and deletion policy,
- cost/capacity implications.

Required evidence should include, as applicable:

```text
features/
├── feature_store_design.md
├── feature_registry.yaml
├── offline_online_mapping.yaml
├── feature_freshness_slos.yaml
├── training_serving_consistency.md
├── skew_validation.md
└── feature_access_policy.md
```

Do not let a feature store become an ungoverned duplicate data platform. Canonical source data remains authoritative; the feature layer contains governed derived signals with explicit provenance.

---

# 7. AI / ML Engineering Standard

Do not start with the fanciest model.

Progress from:

1. trusted visibility,
2. approved process/data baseline and source/process thresholds,
3. governed feature definitions and validated training datasets,
4. feature baseline / drift-reference validation,
5. governed feature management / feature-store capability where required,
6. anomaly/change detection,
7. supervised prediction,
8. explanation,
9. model calibration and evidence-derived decision/abstention thresholds,
10. historical case retrieval,
11. causal analysis,
12. digital-twin/counterfactual methods,
13. prescriptive optimization,
14. agent-assisted investigation,
15. bounded autonomy only after separate assurance.

Use temporal validation for time-dependent systems.

Evaluate:

- calibration,
- class imbalance,
- warning horizon,
- robustness,
- drift,
- domain shift,
- portability,
- false-alert burden,
- abstention behavior.

Generative AI should not be placed in a safety/quality-critical numeric prediction path without strong justification and controls.

---

# 8. Security and Threat Modeling

For substantial systems, produce a threat model before deployment.

Cover:

- identity,
- secrets,
- data integrity,
- model/artifact integrity,
- supply chain,
- API abuse,
- prompt/tool abuse,
- network boundaries,
- tenant/site isolation,
- exfiltration,
- availability,
- rollback,
- evidence integrity.

For OT/cyber-physical systems:

- preserve operational safety and reliability,
- use segmented trust zones,
- prefer read-oriented integration first,
- never create an undocumented cloud-to-control write path,
- ensure AI failure does not impair base plant control.

---

# 9. MLOps and Release Engineering

Required production controls include:

- code versioning,
- data version/provenance,
- schema/version contracts,
- feature versioning,
- model registry,
- release manifest,
- CI/CD,
- validation gates,
- observability,
- drift monitoring,
- rollback,
- runbooks,
- incident response,
- audit trail.

Recommended release progression:

```text
G0 Discovery / Data Readiness
G1 Architecture / Reproducible Baseline
G2 Offline V&V
G3 Shadow
G4 Advisory Canary
G5 Production Advisory
G6 Scale-Out
G7 Bounded Automation only after separate safety assurance
```

Do not declare GO based on synthetic tests alone. Do not declare GO while any applicable critical threshold is failed, unverified, or supported only by a weakened post-hoc criterion.

---

# 10. SLO and Observability Standard

Define SLOs from operational needs, not arbitrary defaults.

Track where relevant:

- data freshness,
- data completeness,
- pipeline latency,
- prediction latency,
- service availability,
- calibration,
- false-alert burden,
- traceability coverage,
- rollback time,
- recovery time,
- security telemetry,
- evidence completeness.

Required dashboard classes generally include:

- operational risk,
- data health,
- model performance,
- drift/domain shift,
- human disposition,
- release evidence,
- security/integration health,
- business KPI baseline and realized impact.

---

# 11. Capacity Planning

Do not select cloud SKUs before workload evidence exists.

Measure or parameterize:

- events/sec,
- payload size,
- burst factor,
- retention,
- records/day,
- storage/day,
- model scoring frequency,
- concurrency,
- feature width,
- training history depth,
- graph entity/edge counts,
- disconnected-edge recovery buffer,
- network bandwidth,
- RPO/RTO.

If values are unknown, state that they are unknown and preserve formulas rather than inventing numbers.

---

# 12. Architecture Trade Studies and ADRs

Before final cloud mapping, document major trade studies such as:

- stream vs batch,
- edge vs centralized,
- relational vs graph,
- pure ML vs physics-informed/hybrid,
- global vs site-specific models,
- advisory vs direct control,
- monolithic vs composable twin,
- LLM in critical path vs investigation-only,
- tightly coupled cloud vs portable core.

Capture accepted decisions in ADRs.

Each ADR should contain:

- context,
- decision,
- alternatives,
- rationale,
- consequences,
- risks,
- verification or review trigger.

---

# 13. Cloud Entry Gates

Do not proceed to Azure/AWS implementation until the project has enough evidence to make product selection defensible.

Typical entry criteria:

- canonical schemas/data contracts versioned,
- event rate and retention measured,
- latency and warning-horizon defined,
- trust boundary approved,
- identity/RBAC matrix defined,
- data classification/retention documented,
- model release/evidence manifest defined,
- RPO/RTO defined,
- pilot acceptance thresholds defined,
- trade studies/ADRs accepted,
- threat model reviewed,
- cost-model inputs measured.

At this point, cloud mapping becomes an implementation exercise rather than architecture-by-product-selection.

---

# 14. Cloud Implementation Standard

When the cloud gate is reached, preserve the lifecycle order in Section 1.1. Cloud mapping and platform engineering precede workload-specific data and AI implementation.

1. map every cloud-agnostic capability to candidate managed services,
2. compare alternatives and document the service-selection rationale,
3. define tenant/account hierarchy, management groups/OUs, subscriptions/accounts, region/residency and environment boundaries,
4. define network topology, DNS, ingress/egress and private-access patterns,
5. define identity/RBAC, privileged access and workload-identity patterns,
6. define encryption/key management, secrets handling, data classification and retention controls,
7. define centralized logging, metrics, traces, audit evidence and security-monitoring patterns,
8. define backup/restore, RPO/RTO, degraded-mode and DR architecture requirements,
9. define cost allocation, budgets, quota/capacity assumptions and FinOps controls,
10. build the **Platform Engineering foundation**: reusable IaC modules, CI/CD, policy-as-code, registries, artifact promotion, supply-chain controls, environment promotion and developer/workspace standards,
11. validate the landing zone/platform foundation in non-production before workload deployment,
12. deploy workload landing-zone resources using the platform's approved patterns,
13. implement governed data/streaming services and validate data contracts, lineage, quality and retention,
14. establish the **Process/Data Baseline** from measured source/contextualized data and derive only source/process/data-quality/capacity thresholds that are defensible at this stage; document version and recalibration triggers,
15. implement **Feature Engineering**: define/version transformations, prove point-in-time correctness, prevent leakage, validate feature quality, preserve feature lineage, and create reproducible training datasets,
16. establish the **Feature Baseline & Validation**: version feature reference distributions, expected ranges, freshness/missingness behavior, segment baselines, drift-reference statistics, and training-set reproducibility evidence,
17. implement **Feature Store / Feature Management** where required: catalog/register features, govern ownership/versioning, provide offline historical retrieval and online serving only where justified, enforce freshness/access controls, and validate training-serving consistency/skew,
18. implement ML/MLOps/AI services; derive model score, calibrated-risk, classification, abstention, and model-drift thresholds from model-validation evidence,
19. implement application/decision-intelligence services and validate alert severity, escalation, and action thresholds against operational/human-factor requirements,
20. execute security/privacy/observability assurance,
21. execute performance, capacity, reliability, backup/restore, recovery and failure-injection tests,
22. capture release evidence and resolve exceptions,
23. only then promote to production.

Do not use cloud implementation as a reason to skip cloud-agnostic design, and do not let an individual workload own the enterprise platform foundation. Shared platform capabilities belong to the platform layer; workload repositories consume them and contain only workload-specific infrastructure where practical.

---

# 15. VS Code and Developer Experience

DME repositories should be VS Code ready.

The **developer workspace standard is a Platform Engineering deliverable**. A lightweight workspace scaffold may exist earlier for architecture/documentation work, but the authoritative workspace configuration, toolchain policy and reproducible developer environment are finalized during Platform Engineering and inherited by workload repositories.

Include where appropriate:

- `.code-workspace`,
- `.vscode/extensions.json`,
- `.vscode/settings.json`,
- `.vscode/tasks.json`,
- `.vscode/launch.json` when debugging profiles are needed,
- `.devcontainer/` when a reproducible containerized workstation is appropriate,