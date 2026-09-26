# AI/ML and Decision Intelligence Architecture

## Table of contents

- [Capability hierarchy](#capability-hierarchy)
- [Model families](#model-families)
- [Validation strategy](#validation-strategy)
- [Decision intelligence](#decision-intelligence)
- [Human-in-the-loop](#human-in-the-loop)

## Capability hierarchy

1. data visibility
2. statistical process monitoring
3. anomaly detection
4. predictive quality
5. yield/scrap prediction
6. root-cause intelligence
7. causal inference
8. digital-twin / counterfactual simulation
9. prescriptive optimization
10. agent-assisted investigation
11. bounded autonomy only after separate safety assurance

## Model families

Model selection remains evidence-driven. Candidate families include:
- multivariate statistical monitoring
- Isolation Forest / autoencoder anomaly models
- gradient-boosted trees
- temporal neural/state-space models
- change-point detection
- survival/prognostics
- causal graphical models
- graph reasoning
- computer vision
- physics-informed/hybrid models

## Validation strategy

Production candidate models require:
- chronological/temporal validation
- leakage controls
- calibration assessment
- class-imbalance-aware metrics
- drift/domain-shift testing
- line/site portability analysis
- reproducibility
- versioned evidence manifest
- rollback proof

## Decision intelligence

Predictions must produce evidence, not opaque action. Where appropriate the system evaluates counterfactuals such as:

`current risk → candidate bounded change → simulated quality/yield/throughput effect`

Recommendations remain subject to policy and human authority.

## Human-in-the-loop

Approve, modify and reject are mutually exclusive human outcomes and therefore use an exclusive merge, not a synchronization join. Parallel gateways are reserved for genuinely concurrent work that must synchronize.
