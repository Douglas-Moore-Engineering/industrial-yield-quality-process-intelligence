# Model improvement and independent acceptance

The runtime build and the model-quality gate are separate. The user's completion requirement includes passing the quality criteria; a successful job or passing unit tests does not satisfy it.

## Fixed criteria

- Recall at least 0.50.
- False alerts divided by **all evaluated rows** at most 0.10. This preserves the existing denominator; it is not precision or the false-positive rate among negatives.
- Evaluate runtime eligibility as well as model scores. An abstained failure remains a missed failure in the recall denominator.
- No actual plant-control or production authority is granted by a reference benchmark pass.

The statistical decision cutoff is learned on development/calibration data; the acceptance criteria above are unchanged. The cutoff is frozen before independent confirmation. Boundaries are placed between distinct score groups to avoid last-bit floating-point differences changing a tied boundary decision.

## Experiment record

1. [V2 protocol](../governance/model-experiment-v2.json): 19 fixed candidates were compared with three forward folds within the original training partition. The selected 100-feature logistic candidate failed later calibration. No new data was read.
2. A calibration screen of those candidates and a 48-setting development exploration of causal rolling deviations, squared features and RBF models did not reach the criterion. These explorations are not independent tests.
3. [V3 protocol](../governance/model-experiment-v3.json): all original SECOM rows were explicitly reclassified as exposed development data. Classifiers fit the first 1,250 rows; the former 317-row test set became development validation/calibration. The same 19-model pool and then a 40-setting sparse-logistic refinement were evaluated. No result from this reclassified set is called fresh acceptance.
4. The frozen candidate `66587bfb754049a71963a17a84300510` uses 20 selected sensors and C=0.003 with balanced class weights. Preprocessing/feature selection use classifier-training rows only. Calibration and cutoff fitting use development validation. It detects 9/17 failures with 28 false alerts over 317 rows, including four abstentions: recall 0.5294 and false-alert fraction 0.08833. Raw classifier recall is higher; the reported gate deliberately uses the lower runtime-guarded result.
5. The user reports a separate unseen dataset. Its location/format is not yet supplied. It has not been inspected or used. Fresh confirmation and any replacement of the Azure baseline remain pending.

The modest development margin and small failure count are material limitations. The confirmation report includes Wilson intervals as uncertainty information, without quietly changing the agreed point-estimate gate. Neither development metrics nor a future small-sample pass establishes plant-level reliability.

## Frozen artifacts

The numeric model, preprocessing, feature order, calibration and decision threshold are under ignored `artifacts/candidate-models/<model-id>/`. `freeze.json` records the model manifest hash and freeze time. The compatible three-file model manifest permits the existing checksum verifier to reject modification. Failed and superseded candidate bundles are retained; use the current candidate ID above.

Development results are under ignored `artifacts/model-development/`. [Sanitized current evidence](../.azure/candidate-acceptance.json) contains no account identifiers or raw records. Existing deployed reference AI evidence describes the earlier baseline and is preserved rather than overwritten.

## Independent confirmation format

The implemented confirmation reader accepts a UTF-8 CSV with exactly:

`event_time,failure,sensor_1,...,sensor_590`

`failure` is 0 (pass) or 1 (failure). Timestamps require explicit timezones. Empty or NaN sensor values remain missing; infinities are rejected. Sensor meanings and process identity must match the development source; a matching column count alone is not proof of the same process. Once the user identifies the actual source format, adapt it without inspecting outcomes for tuning. Do not substitute a different dataset and call that SECOM confirmation.

```powershell
$env:PYTHONPATH = 'src'
python -m iyqpis.confirmation artifacts/candidate-models/66587bfb754049a71963a17a84300510 artifacts/data-runs/281f7c0541e36345c52c8b7ee51e14f8 <unseen-data.csv> artifacts/confirmation --declare-previously-unseen
```

The command refuses an unverified or calibration-failed bundle before opening unseen rows. It reserves the candidate evaluation before reading records, rejects exact feature-row overlap with exposed data and repeated confirmation rows, requires a later source period, and evaluates the frozen weights and cutoff without fitting anything. It reports historical replay eligibility; it does not prove live source freshness or feature availability before disposition. Caller provenance review is still required.

A candidate-local reservation refuses a second confirmation call, including one with another output directory. This is a local operator safeguard, not an enterprise tamper-proof evaluation service. Keep rejected/evaluated receipts; once outcomes are inspected, that data must not be relabeled as unseen. A failed confirmation means the system is not complete and requires further development plus new independent confirmation evidence.

## Verification and deployment boundary

73 software tests pass, including budget/tie handling, counting abstentions, temporal separation, refusal before reading unseen data, one-shot reservation, overlap rejection and preserving the frozen cutoff. The new candidate is not deployed and no additional Azure compute was started for these development experiments. Only after valid independent confirmation should the exact frozen model be packaged, verified in the existing Azure shadow runtime and compared with the confirmation predictions. Do not retrain or change its cutoff during deployment.

Method reference: [scikit-learn decision-threshold guidance](https://scikit-learn.org/1.5/modules/classification_threshold.html) distinguishes fitting the classifier from fitting its decision rule and warns against reusing classifier-training data for that tuning.
