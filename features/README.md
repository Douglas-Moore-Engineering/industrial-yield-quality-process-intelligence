# Lenze feature governance

This catalog governs the 16 publisher-precomputed columns used by the frozen reference model. It does not establish that the upstream extraction is reproducible or point-in-time correct. No raw-audio extraction implementation has been independently validated.

The machine-readable [catalog](lenze-catalog.json) records source and identity transformation for each feature. The [baseline](lenze-baseline-v1.json) profiles publisher training records only, including the original calibration subset. It is retrospective evidence assembled after model evaluation, not a claim that these gates passed before training. It must not be used to revise the cutoff against the inspected test set.

Owner: reference engineering role. Production reviewer/approver: unassigned. Units, extraction windows and source formulas remain unverified; column names are not sufficient to establish physical definitions. Identifier, class/quality labels, perceived category, dataset partition and variant identifiers are excluded from model predictors. All six optimized features remain excluded.

## Quality and lifecycle rules

- Source SHA256 must match the frozen manifest; identifiers must be unique and joins complete.
- All 16 values must be finite and supplied in the frozen feature order. No imputation or inferred units.
- Recorded quantiles and ranges describe normal training examples; they are not approved process limits or automatic rejection thresholds.
- New sources, extraction versions or feature definitions require a new version and review. Preserve this baseline and frozen model for rollback.
- Production feature freshness, point-in-time correctness, raw-to-feature lineage and skew controls remain unverified.

## Feature management decision

Use a versioned file catalog and immutable model/source manifests for this single on-demand reference workload. A managed online feature store and TTL/cache policy are not applicable to this execution pattern; no online feature serving is implemented. Revisit when multiple consumers, live sources or low-latency serving are authorized. This is an engineering applicability recommendation, not recorded stakeholder approval.

Runtime access inherits the existing private registry/storage and managed-identity controls. Repository evidence contains aggregate statistics only. The catalog does not authorize broader access, retention changes, deployment or model promotion.
