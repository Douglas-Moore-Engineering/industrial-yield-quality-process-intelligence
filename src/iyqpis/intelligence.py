"""Versioned SECOM quality benchmark. Sample-only: never authorizes plant actions.

Models are numeric JSON, not executable pickle. Fit preprocessing on training
only, calibrate on a later partition, and evaluate once on the final partition.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import tempfile
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.exceptions import ConvergenceWarning

from iyqpis.pipeline import digest, verify_run, write_json

FEATURES = [f"sensor_{i}" for i in range(1, 591)]
FEATURE_VERSION = "secom-sensors-v1"


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def load_features(run: Path):
    """Join only explicit sample row identifiers; never fabricate lot genealogy."""
    manifest = verify_run(run)
    if "secom" not in manifest["datasets"]:
        raise ValueError("SECOM is absent from the verified data run")
    declared = {a["path"] for a in manifest["artifacts"]}
    required = {"validated/secom/telemetry.jsonl", "validated/secom/quality_result.jsonl"}
    if not required <= declared:
        raise ValueError("Required features/labels are not covered by the manifest")
    rows, labels = {}, {}
    for line in (run / "validated/secom/quality_result.jsonl").open(encoding="utf-8"):
        record = json.loads(line)
        key = int(record["quality_result_id"].removeprefix("secom-"))
        if key in labels or record["disposition"] not in {"PASS", "FAIL"}:
            raise ValueError("Duplicate or invalid quality label")
        labels[key] = (record["event_time"], int(record["disposition"] == "FAIL"))
    for line in (run / "validated/secom/telemetry.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        key = r["sequence_number"]
        if key not in labels or r["event_time"] != labels[key][0] or r["asset_id"] != "secom-line-01":
            raise ValueError("Feature/label alignment mismatch")
        index = int(r["tag_id"].removeprefix("sensor_")) - 1
        if index not in range(len(FEATURES)):
            raise ValueError("Unknown sensor")
        row = rows.setdefault(key, {})
        if index in row:
            raise ValueError("Duplicate sensor")
        value = float(r["value"])
        if not np.isfinite(value):
            raise ValueError("Nonfinite validated sensor")
        row[index] = value if r["quality_flag"] == "GOOD" else np.nan
    if set(rows) != set(labels) or any(len(row) != len(FEATURES) for row in rows.values()):
        raise ValueError("Incomplete feature coverage")
    keys = sorted(rows, key=lambda key: (labels[key][0], key))
    x = np.array([[rows[k][j] for j in range(len(FEATURES))] for k in keys])
    return x, np.array([labels[k][1] for k in keys]), [labels[k][0] for k in keys], keys, manifest


def temporal_partitions(times):
    unique = sorted(set(times))
    if len(unique) < 15 or list(times) != sorted(times):
        raise ValueError("Need ordered timestamps with at least 15 distinct values")
    boundaries = unique[int(len(unique) * .6)], unique[int(len(unique) * .8)]
    groups = [np.array([i for i, t in enumerate(times) if predicate(t)]) for predicate in
              (lambda t: t < boundaries[0], lambda t: boundaries[0] <= t < boundaries[1],
               lambda t: t >= boundaries[1])]
    if any(len(group) == 0 for group in groups):
        raise ValueError("Empty temporal partition")
    return groups


def fit_preprocessor(x):
    keep = np.array([i for i in range(x.shape[1]) if np.isfinite(x[:, i]).any()])
    if not len(keep):
        raise ValueError("No observed training features")
    medians = np.nanmedian(x[:, keep], axis=0)
    filled = np.where(np.isnan(x[:, keep]), medians, x[:, keep])
    scales = filled.std(axis=0)
    selected = scales > 1e-12
    if not selected.any():
        raise ValueError("No variable training features")
    return {"indices": keep[selected].tolist(), "median": medians[selected].tolist(),
            "mean": filled.mean(axis=0)[selected].tolist(), "scale": scales[selected].tolist()}


def transform(x, prep):
    values = x[:, prep["indices"]]
    return (np.where(np.isnan(values), prep["median"], values) - prep["mean"]) / prep["scale"]


def sigmoid(value):
    return 1 / (1 + np.exp(-np.clip(value, -700, 700)))


def probabilities(model, x):
    z = transform(x, model["preprocessing"])
    raw = z @ np.array(model["coefficients"]) + model["intercept"]
    return sigmoid(raw * model["calibration"]["slope"] + model["calibration"]["intercept"])


def metrics(y, probability, threshold):
    alerts = probability >= threshold
    reliability = []
    ece = 0.
    for left in np.linspace(0, .9, 10):
        mask = (probability >= left) & (probability < left + .1 if left < .9 else probability <= 1)
        if mask.any():
            observed, predicted = float(y[mask].mean()), float(probability[mask].mean())
            ece += mask.mean() * abs(observed - predicted)
            reliability.append({"count": int(mask.sum()), "observed": observed, "predicted": predicted})
    positives = int(y.sum())
    return {"rows": len(y), "failures": positives, "prevalence": float(y.mean()),
            "average_precision": float(average_precision_score(y, probability)) if positives else None,
            "roc_auc": float(roc_auc_score(y, probability)) if len(set(y)) == 2 else None,
            "brier": float(brier_score_loss(y, probability)), "ece_10_bins": float(ece),
            "reliability": reliability, "alert_fraction": float(alerts.mean()),
            "recall": float(y[alerts].sum() / positives) if positives else None,
            "false_alerts": int(((y == 0) & alerts).sum()), "threshold": float(threshold)}


def train(run: Path, output: Path):
    run, output = run.resolve(), output.resolve()
    if output == run or output.is_relative_to(run):
        raise ValueError("Models must be written outside the verified input run")
    x, y, times, keys, source = load_features(run)
    train_idx, calibration_idx, test_idx = temporal_partitions(times)
    for indices in (train_idx, calibration_idx, test_idx):
        if len(set(y[indices])) != 2:
            raise ValueError("Each temporal partition must contain both classes")
    prep = fit_preprocessor(x[train_idx])
    estimator = LogisticRegression(C=.01, max_iter=2000, random_state=0)
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        estimator.fit(transform(x[train_idx], prep), y[train_idx])
        scores = estimator.decision_function(transform(x[calibration_idx], prep)).reshape(-1, 1)
        calibrator = LogisticRegression(C=1., max_iter=2000, random_state=0).fit(scores, y[calibration_idx])
    model = {"schema_version": 1, "purpose": "sample_quality_benchmark", "production_approved": False,
             "feature_version": FEATURE_VERSION, "features": FEATURES, "source_system": "sample:secom",
             "preprocessing": prep, "coefficients": estimator.coef_[0].tolist(),
             "intercept": float(estimator.intercept_[0]),
             "calibration": {"slope": float(calibrator.coef_[0][0]), "intercept": float(calibrator.intercept_[0])},
             "data_run_id": source["run_id"], "data_manifest_sha256": digest(run / "manifest.json"),
             "code_sha256": digest(Path(__file__)),
             "implementation": {name: digest(Path(__file__).with_name(name)) for name in
                                ("intelligence.py", "operations.py", "reference.py", "azure_intelligence.py")},
             "dependencies_sha256": digest(Path(__file__).resolve().parents[2] / "requirements-ml.txt"),
             "training_parameters": {"classifier_C": .01, "calibration_C": 1., "solver": "lbfgs", "random_state": 0},
             "runtime": {"python": platform.python_version(), "numpy": np.__version__, "sklearn": sklearn.__version__},
             "guardrails": {"max_missing_fraction": .2, "max_abs_standardized_value": 8., "max_age_seconds": 300}}
    # Threshold selection uses calibration data only, not the held-out test labels.
    cal_prob = probabilities(model, x[calibration_idx])
    model["alert_threshold"] = float(np.quantile(cal_prob, .9))
    model_id = fingerprint(model)[:32]
    model["model_id"] = model_id
    test_prob = probabilities(model, x[test_idx])
    baseline = np.full(len(test_idx), float(y[train_idx].mean()))
    report = {"model_id": model_id, "scope": "offline sample benchmark, not production acceptance",
              "split": {name: {"rows": len(ids), "start": times[ids[0]], "end": times[ids[-1]],
                               "sample_ids_sha256": fingerprint([keys[i] for i in ids])}
                        for name, ids in zip(("train", "calibration", "test"), (train_idx, calibration_idx, test_idx))},
              "test": metrics(y[test_idx], test_prob, model["alert_threshold"]),
              "constant_baseline": metrics(y[test_idx], baseline, model["alert_threshold"]),
              "limitations": ["Source timezone assumed UTC", "Sensor availability before disposition unproven",
                              "No lot/run/site holdout identifiers", "No demonstrated warning horizon",
                              "Threshold is a benchmark setting, not plant-approved", "Not a causal or yield model"],
              "production_release": "BLOCKED"}
    report["benchmark_alert_gate"] = {
        "scope": "illustrative software benchmark criterion, not a plant acceptance threshold",
        "minimum_recall": .5, "maximum_false_alert_fraction": .1,
        "passed": bool(report["test"]["recall"] >= .5 and
                       report["test"]["false_alerts"] / report["test"]["rows"] <= .1)}
    output.mkdir(parents=True, exist_ok=True)
    destination = output / model_id
    if destination.exists():
        verify_bundle(destination)
        return destination
    stage = Path(tempfile.mkdtemp(prefix=".pending-", dir=output))
    write_json(stage / "model.json", model)
    write_json(stage / "evaluation.json", report)
    predictions = [{"sample_id": keys[i], "event_time": times[i], "observed_failure": int(y[i]),
                    "shadow_probability": float(p), "model_id": model_id} for i, p in zip(test_idx, test_prob)]
    write_json(stage / "test-predictions.json", predictions)
    write_json(stage / "manifest.json", {"status": "complete", "model_id": model_id,
               "artifacts": [{"path": name, "sha256": digest(stage / name)} for name in
                             ("model.json", "evaluation.json", "test-predictions.json")]})
    stage.rename(destination)
    return destination


def verify_bundle(path):
    path = Path(path).resolve()
    manifest = json.loads((path / "manifest.json").read_text())
    if manifest["status"] != "complete" or manifest["model_id"] != path.name:
        raise ValueError("Invalid model bundle")
    if {a["path"] for a in manifest["artifacts"]} != {"model.json", "evaluation.json", "test-predictions.json"}:
        raise ValueError("Incomplete model manifest")
    for item in manifest["artifacts"]:
        target = (path / item["path"]).resolve()
        if not target.is_relative_to(path) or digest(target) != item["sha256"]:
            raise ValueError("Model artifact checksum mismatch")
    model = json.loads((path / "model.json").read_text())
    unsigned = {k: v for k, v in model.items() if k != "model_id"}
    if model["model_id"] != manifest["model_id"] or fingerprint(unsigned)[:32] != model["model_id"]:
        raise ValueError("Model identity mismatch")
    evaluation = json.loads((path / "evaluation.json").read_text())
    if evaluation["model_id"] != model["model_id"]:
        raise ValueError("Evaluation/model identity mismatch")
    return model


def infer(model, values, event_time, source_system, now=None):
    """Shadow score plus evidence; sample models always abstain from recommendations."""
    now = now or datetime.now(timezone.utc)
    event = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
    if now.tzinfo is None or event.tzinfo is None:
        raise ValueError("Timezone required")
    reasons = ["sample_model_not_approved"]
    if source_system != model["source_system"]:
        reasons.append("unknown_domain")
    age = (now - event).total_seconds()
    if age < 0 or age > model["guardrails"]["max_age_seconds"]:
        reasons.append("future_or_stale_data")
    if set(values) != set(model["features"]):
        reasons.append("feature_contract_mismatch")
    result = {"model_id": model["model_id"], "data_run_id": model["data_run_id"],
              "feature_version": model["feature_version"], "authority_state": "ABSTAIN",
              "mode": "SHADOW", "reasons": reasons, "shadow_probability": None,
              "recommended_action": "No plant action authorized; engineering review only"}
    if len(reasons) > 1:
        return result
    try:
        if any(value is not None and (isinstance(value, bool) or not np.isfinite(float(value))) for value in values.values()):
            raise ValueError("Nonfinite or boolean sensor")
        row = np.array([[np.nan if values[name] is None else float(values[name]) for name in model["features"]]])
    except (ValueError, TypeError):
        result["reasons"].append("invalid_sensor_value")
        return result
    if np.isinf(row).any() or np.isnan(row).mean() > model["guardrails"]["max_missing_fraction"]:
        result["reasons"].append("invalid_or_missing_sensors")
        return result
    z = transform(row, model["preprocessing"])[0]
    if np.max(np.abs(z)) > model["guardrails"]["max_abs_standardized_value"]:
        result["reasons"].append("outside_training_envelope")
        return result
    result["shadow_probability"] = float(probabilities(model, row)[0])
    contribution = z * np.array(model["coefficients"]) * model["calibration"]["slope"]
    result["contributors"] = [{"feature": model["features"][model["preprocessing"]["indices"][i]],
                               "calibrated_log_odds_contribution": float(contribution[i])}
                              for i in np.argsort(np.abs(contribution))[-5:][::-1]]
    result["explanation_scope"] = "Model associations, not causal effects"
    result["evidence_id"] = fingerprint({"model": model["model_id"], "values": values, "event_time": event_time})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_run", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    path = train(args.data_run, args.output)
    print(json.dumps({"status": "complete", "model_id": path.name, "production_release": "BLOCKED"}))


if __name__ == "__main__":
    main()
