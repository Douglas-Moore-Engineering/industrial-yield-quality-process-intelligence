# Testing, Release Gates and Acceptance

## Table of contents

- [Verification strategy](#verification-strategy)
- [Test classes](#test-classes)
- [Release gates](#release-gates)
- [Acceptance criteria](#acceptance-criteria)

## Verification strategy

Verification must cover both software behavior and industrial operating behavior.

## Test classes

- schema and contract tests
- unit tests
- transformation/data-quality tests
- deterministic replay
- temporal model validation
- calibration tests
- drift/domain-shift tests
- integration tests
- genealogy reconstruction
- security and authorization tests
- failure injection
- rollback/restore exercises
- load/capacity tests
- shadow-mode evaluation
- human-review acceptance testing

## Release gates

| Gate | Meaning |
|---|---|
| G0 | Data readiness |
| G1 | Reproducible baseline |
| G2 | Offline model/system V&V |
| G3 | Shadow deployment |
| G4 | Advisory canary |
| G5 | Production advisory |
| G6 | Advanced prescriptive/autonomy gate requiring separate safety assurance |

## Acceptance criteria

A pilot must prove, at minimum:
- reproducible process reconstruction
- validated data quality
- calibrated risk estimates
- warning before final disposition for applicable event classes
- affected-material traceability
- interpretable evidence
- human disposition logging
- drift detection
- complete model/data lineage
- safe failure
- no unauthorized control path
- rollback
- agreed false-alert burden
- process-engineering validation
