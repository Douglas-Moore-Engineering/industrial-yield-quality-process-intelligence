# Architecture Views

The diagrams below render directly on GitHub. Editable Mermaid sources are versioned beside this index.

## Table of contents

- [1. System Context and Authority Boundaries](#1-system-context-and-authority-boundaries)
- [2. Concept of Operations](#2-concept-of-operations)
- [3. Functional Capability Decomposition](#3-functional-capability-decomposition)
- [4. Digital Thread, Genealogy and Evidence Lineage](#4-digital-thread-genealogy-and-evidence-lineage)
- [5. OT / IT Trust Zones and Security Boundary](#5-ot--it-trust-zones-and-security-boundary)
- [6. Governed MLOps and Model Lifecycle](#6-governed-mlops-and-model-lifecycle)
- [7. Human-in-the-Loop Decision Workflow](#7-human-in-the-loop-decision-workflow)
- [8. Threat Model and Defense-in-Depth](#8-threat-model-and-defense-in-depth)
- [9. Requirements Traceability and Verification](#9-requirements-traceability-and-verification)
- [10. Release Pipeline and Promotion Gates](#10-release-pipeline-and-promotion-gates)
- [11. SLO, Observability and Operational Response](#11-slo-observability-and-operational-response)
- [12. Cloud-Agnostic Deployment Topology](#12-cloud-agnostic-deployment-topology)

## 1. System Context and Authority Boundaries

[Edit source](01_system_context.mmd)

```mermaid
flowchart TB
subgraph L1["PLANT / OT"]
  A["Sensors / PLC / DCS / Historian"] --> B["Read Gateway / Buffer"]
end
subgraph L2["INDUSTRIAL DATA"]
  B --> C["Raw / Immutable"]
  C --> D["Validated / Contextualized"]
  D --> E["Digital Thread / Evidence"]
end
subgraph L3["AI / ANALYTICS"]
  E --> F["Features / Models / Twin"]
  F --> G["Risk + Evidence"]
end
subgraph L4["DECISION / OPERATIONS"]
  G --> H{"Guardrails pass?"}
  H -->|Yes| I["Operator / Engineer Review"]
  H -->|No| J["Abstain / Log"]
  I --> K["Authorized Existing Work / Control"]
end
K -. "Outcome feedback" .-> G
```

## 2. Concept of Operations

[Edit source](02_conops.mmd)

```mermaid
flowchart TB
subgraph L1["OBSERVE"]
  A["Process Telemetry"] --> B["Production Context"]
  B --> C["Quality / Maintenance Context"]
end
subgraph L2["UNDERSTAND"]
  C --> D["Contextualize Manufacturing State"]
  D --> E["Detect Anomaly / Drift"]
  E --> F["Predict Yield / Quality Risk"]
end
subgraph L3["DECIDE"]
  F --> G["Explain Drivers"]
  G --> H["Simulate / Counterfactual"]
  H --> I["Recommend Bounded Action"]
end
subgraph L4["AUTHORIZE & LEARN"]
  I --> J{"Human Decision"}
  J -->|Approve / Modify| K["Authorized Action"]
  J -->|Reject| L["Investigate / Log"]
  K --> M["Verify Outcome"]
  M --> N["Learn / Update Evidence"]
end
N -.-> D
```

## 3. Functional Capability Decomposition

[Edit source](03_functional_decomposition.mmd)

```mermaid
flowchart TB
subgraph L1["DATA FOUNDATION"]
  A["Ingest"] --> B["Validate"]
  B --> C["Contextualize"]
  C --> D["Genealogy / Evidence"]
end
subgraph L2["INTELLIGENCE"]
  D --> E["Process Health"]
  D --> F["Predictive Quality"]
  D --> G["Yield / Scrap Risk"]
  E --> H["Root Cause"]
  F --> H
  G --> H
end
subgraph L3["DECISION"]
  H --> I["Counterfactual / Twin"]
  I --> J["Recommendation"]
  J --> K["Policy Guardrails"]
end
subgraph L4["OPERATIONS"]
  K --> L["Human Disposition"]
  L --> M["Outcome Ledger"]
  M --> N["Monitoring / Learning"]
end
```

## 4. Digital Thread, Genealogy and Evidence Lineage

[Edit source](04_digital_thread.mmd)

```mermaid
flowchart TB
subgraph L1["MATERIAL"]
  A["Supplier / Lot"] --> B["Material Batch"]
end
subgraph L2["PRODUCTION"]
  B --> C["Campaign / Run"]
  C --> D["Process Window"]
  D --> E["Equipment State"]
end
subgraph L3["PRODUCT"]
  E --> F["Intermediate Product"]
  F --> G["Finished Product"]
end
subgraph L4["QUALITY & EVIDENCE"]
  G --> H["Quality Test"]
  H --> I["Disposition"]
  D -.-> J["Prediction / Alert"]
  E -.-> J
  J --> K["Recommendation / Decision"]
  K --> I
end
```

## 5. OT / IT Trust Zones and Security Boundary

[Edit source](05_ot_it_security.mmd)

```mermaid
flowchart TB
subgraph L1["LEVEL 0/1 — FIELD"]
  A["Sensors / Actuators"]
end
subgraph L2["LEVEL 2 — CONTROL"]
  A --> B["PLC / DCS / Local Control"]
end
subgraph L3["LEVEL 3 — OPERATIONS"]
  B --> C["SCADA / Historian / MES"]
end
subgraph L4["INDUSTRIAL DMZ"]
  C --> D["Read Gateway / Broker / Buffer"]
end
subgraph L5["ENTERPRISE / AI"]
  D --> E["Industrial Data Platform"]
  E --> F["AI / MLOps / Analytics"]
end
F -. "No direct AI control write" .-x B
```

## 6. Governed MLOps and Model Lifecycle

[Edit source](06_mlops_lifecycle.mmd)

```mermaid
flowchart TB
subgraph L1["DEVELOP"]
  A["Data / Feature Version"] --> B["Train"]
  B --> C["Validate"]
end
subgraph L2["EVIDENCE"]
  C --> D["Calibration / Explainability"]
  D --> E["Safety / Robustness"]
  E --> F["Release Manifest"]
end
subgraph L3["PROMOTE"]
  F --> G{"Gate pass?"}
  G -->|Yes| H["Registry / Approved Version"]
  G -->|No| I["Remediate"]
  I -.-> B
end
subgraph L4["OPERATE"]
  H --> J["Shadow / Canary / Advisory"]
  J --> K["Monitor Drift / SLO"]
  K --> L{"Rollback needed?"}
  L -->|Yes| H
  L -->|No| J
end
```

## 7. Human-in-the-Loop Decision Workflow

[Edit source](07_hitl_workflow.mmd)

```mermaid
flowchart TB
subgraph L1["AI / ANALYTICS"]
  A1["Rising Process Risk"] --> A2["Risk + Evidence"] --> A3["Candidate Bounded Action"]
end
subgraph L2["POLICY ENGINE"]
  A3 --> P1["Freshness / Data Quality"] --> P2["Operating Envelope"] --> P3["Action Authorization"] --> D1{"Guardrails pass?"}
end
subgraph L3["OPERATOR / ENGINEER"]
  D1 -->|Yes| H1(["Review Evidence + Recommendation"]) --> D2{"Decision?"}
  D2 -->|Approve| H2["Approve"]
  D2 -->|Modify| H3["Modify"]
  D2 -->|Reject / Investigate| H4["Reject / Investigate"]
  H2 --> M1{"×"}
  H3 --> M1
end
subgraph L4["AUTHORIZED OPERATIONS & LEARNING"]
  M1 --> O1["Existing Work / Control"] --> O2["Verify Response"] --> O3["Decision / Outcome Ledger"] --> O4["Feedback to Models / Rules"]
  H4 --> O3
  D1 -->|No — abstain| O3
end
O4 -. "Learning signal" .-> A2
```

## 8. Threat Model and Defense-in-Depth

[Edit source](08_threat_model.mmd)

```mermaid
flowchart TB
subgraph L1["THREAT SOURCES"]
  A["External Attacker"] --> D["Threat Correlation"]
  B["Credential Misuse"] --> D
  C["Supply Chain / Misconfiguration"] --> D
end
subgraph L2["ATTACK PATHS"]
  D --> E["Identity / API Abuse"]
  D --> F["Telemetry / Label Tampering"]
  D --> G["Model / Artifact Compromise"]
end
subgraph L3["PROTECTED ASSETS"]
  E --> H["OT Safety / Availability"]
  F --> I["Manufacturing Data Integrity"]
  G --> J["Model / Decision Integrity"]
end
subgraph L4["CONTROLS"]
  H --> K["Segmentation / IDMZ"]
  I --> L["Validation / Provenance"]
  J --> M["Signed Artifacts / HITL"]
end
```

## 9. Requirements Traceability and Verification

[Edit source](09_traceability.mmd)

```mermaid
flowchart TB
subgraph L1["BUSINESS NEED"]
  A["Increase Conforming Yield"]
  B["Reduce Diagnosis Time"]
  C["Preserve Safe Operations"]
end
subgraph L2["SYSTEM REQUIREMENTS"]
  A --> D["Predict Risk"]
  B --> E["Trace Material / Evidence"]
  C --> F["Safety / Fail-safe"]
end
subgraph L3["ARCHITECTURE"]
  D --> G["Predictive Service"]
  E --> H["Digital Thread / Evidence"]
  F --> I["Policy / HITL / Degraded Mode"]
end
subgraph L4["VERIFICATION"]
  G --> J["Temporal Holdout + Calibration"]
  H --> K["Genealogy Reconstruction"]
  I --> L["Safety / Outage / Audit Tests"]
end
```

## 10. Release Pipeline and Promotion Gates

[Edit source](10_release_pipeline.mmd)

```mermaid
flowchart TB
subgraph L1["ENGINEERING"]
  A["Code / Model / Schema Change"] --> B["Peer Review"] --> C{"Parallel validation"}
  C --> D["Unit / Contract"]
  C --> E["Integration / Replay"]
  C --> F["Security / Dependency"]
  D --> G{"All evidence complete?"}
  E --> G
  F --> G
end
subgraph L2["PROMOTION GATES"]
  G --> H["G0 Data Readiness"] --> I["G1 Reproducible Baseline"] --> J["G2 Offline V&V"] --> K["G3 Shadow"] --> L["G4 Advisory Canary"] --> M["G5 Production Advisory"]
end
subgraph L3["RELEASE AUTHORITY"]
  M --> N{"Gate criteria satisfied?"}
  N -->|Yes| O["Promote"]
  N -->|No| P["Hold / Remediate"]
  P -.-> A
end
```

## 11. SLO, Observability and Operational Response

[Edit source](11_observability.mmd)

```mermaid
flowchart TB
subgraph L1["HEALTH SIGNALS"]
  A["Pipeline / Ingestion"] --> E["Observability Aggregator"]
  B["Data Quality / Freshness"] --> E
  C["Model / Drift / Calibration"] --> E
  D["API / Service Health"] --> E
end
subgraph L2["SLO EVALUATION"]
  E --> F["Freshness SLO"]
  E --> G["Prediction Availability / Latency"]
  E --> H["False Alert / Calibration Guardrail"]
  F --> I{"SLO / guardrail breached?"}
  G --> I
  H --> I
end
subgraph L3["RESPONSE"]
  I -->|Yes| J["Alert / Page"] --> K["Triage Runbook"] --> L["Degraded / Abstain Mode"] --> M["Recover / Rollback"]
  I -->|No| E
end
subgraph L4["IMPROVEMENT"]
  M --> N["Incident Record"] --> O["Post-incident Review"] --> P["Corrective Action Backlog"]
end
```

## 12. Cloud-Agnostic Deployment Topology

[Edit source](12_deployment_topology.mmd)

```mermaid
flowchart TB
subgraph L1["PLANT / EDGE RUNTIME"]
  A["PLC / DCS / Historian / MES"] --> B["Read Gateway + Buffer"] --> C["Local Cache / Optional Edge Inference"]
end
subgraph L2["INDUSTRIAL DATA PLATFORM"]
  C --> D["Raw / Immutable"] --> E["Validated / Contextualized"] --> F["Digital Thread / Evidence"]
end
subgraph L3["AI / DECISION PLATFORM"]
  F --> G["Features / Training Data"] --> H["Model / Twin Services"] --> I["Decision / Investigation APIs"]
end
subgraph L4["USER & GOVERNANCE"]
  I --> J["Operations / Engineering App"] --> K["HITL / Decision Ledger"]
  L["MLOps / Security / Observability"] -.-> H
  L -.-> D
end
K -. "No direct AI write" .-x A
```
