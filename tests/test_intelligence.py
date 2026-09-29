import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3

import numpy as np
import pytest

from iyqpis.intelligence import (fingerprint, fit_preprocessor, infer, metrics,
                                 temporal_partitions, transform, verify_bundle)
from iyqpis.operations import (Ledger, affected_material, comparable_cases, monitor_model,
                               process_baseline, process_monitor, production_gate)
from iyqpis.pipeline import digest, write_json


def model():
    return {"model_id": "fixture", "data_run_id": "reference", "feature_version": "fixture-v1",
            "source_system": "sample:fixture", "features": ["x", "y"],
            "preprocessing": {"indices": [0, 1], "median": [0, 0], "mean": [0, 0], "scale": [1, 1]},
            "coefficients": [1., -1.], "intercept": 0., "calibration": {"slope": 1., "intercept": 0.},
            "guardrails": {"max_missing_fraction": .2, "max_abs_standardized_value": 8., "max_age_seconds": 300},
            "alert_threshold": .5, "production_approved": False}


def bundle(root, coefficient=1.):
    value = model()
    del value["model_id"]
    value["coefficients"][0] = coefficient
    value["model_id"] = fingerprint(value)[:32]
    path = root / value["model_id"]
    path.mkdir()
    write_json(path / "model.json", value)
    write_json(path / "evaluation.json", {"model_id": value["model_id"]})
    write_json(path / "test-predictions.json", [])
    write_json(path / "manifest.json", {"status": "complete", "model_id": path.name,
               "artifacts": [{"path": n, "sha256": digest(path / n)} for n in
                             ("model.json", "evaluation.json", "test-predictions.json")]})
    return path


def test_temporal_split_keeps_equal_timestamps_together():
    times = [f"2026-01-{i:02}T00:00:00Z" for i in range(1, 21) for _ in range(2)]
    a, b, c = temporal_partitions(times)
    assert times[a[-1]] < times[b[0]] < times[c[0]]
    assert times[b[-1]] < times[c[0]]
    assert len(set(a) | set(b) | set(c)) == len(times)
    with pytest.raises(ValueError):
        temporal_partitions(times[::-1])


def test_preprocessing_does_not_learn_from_future_or_missing_columns():
    train = np.array([[1., np.nan, 4.], [3., np.nan, 4.]])
    prep = fit_preprocessor(train)
    assert prep["indices"] == [0]
    assert prep["median"] == [2.]
    assert transform(np.array([[100., 9., 4.]]), prep)[0, 0] == 98.


def test_shadow_never_authorizes_control_even_if_flag_tampered():
    value = model()
    value["production_approved"] = True
    result = infer(value, {"x": 1., "y": 0.}, "2026-01-01T00:00:00Z", "sample:fixture",
                   now=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert result["authority_state"] == "ABSTAIN"
    assert result["shadow_probability"] > .5
    assert result["contributors"][0]["feature"] == "x"


@pytest.mark.parametrize("values,event,source,reason", [
    ({"x": None, "y": 0}, "2026-01-01T00:00:00Z", "sample:fixture", "invalid_or_missing_sensors"),
    ({"x": float('nan'), "y": 0}, "2026-01-01T00:00:00Z", "sample:fixture", "invalid_sensor_value"),
    ({"x": float('inf'), "y": 0}, "2026-01-01T00:00:00Z", "sample:fixture", "invalid_sensor_value"),
    ({"x": True, "y": 0}, "2026-01-01T00:00:00Z", "sample:fixture", "invalid_sensor_value"),
    ({"x": 99, "y": 0}, "2026-01-01T00:00:00Z", "sample:fixture", "outside_training_envelope"),
    ({"x": 1}, "2026-01-01T00:00:00Z", "sample:fixture", "feature_contract_mismatch"),
    ({"x": 1, "y": 0}, "2025-01-01T00:00:00Z", "sample:fixture", "future_or_stale_data"),
    ({"x": 1, "y": 0}, "2027-01-01T00:00:00Z", "sample:fixture", "future_or_stale_data"),
    ({"x": 1, "y": 0}, "2026-01-01T00:00:00Z", "customer:unknown", "unknown_domain"),
])
def test_invalid_inputs_abstain(values, event, source, reason):
    result = infer(model(), values, event, source, now=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert result["shadow_probability"] is None and reason in result["reasons"]


def test_metrics_include_calibration_and_false_alerts():
    result = metrics(np.array([0, 1, 0, 1]), np.array([.1, .9, .8, .2]), .5)
    assert result["false_alerts"] == 1 and result["recall"] == .5
    assert result["brier"] == pytest.approx(.325)


def test_corrupt_bundle_rejected(tmp_path):
    path = bundle(tmp_path)
    assert verify_bundle(path)["model_id"] == path.name
    (path / "model.json").write_text('{}')
    with pytest.raises(ValueError):
        verify_bundle(path)


def test_lifecycle_rollback_and_production_refusal(tmp_path):
    a, b = bundle(tmp_path, 1.), bundle(tmp_path, 2.)
    ledger = Ledger(tmp_path / 'ledger.sqlite')
    try:
        for path in (a, b):
            ledger.activate(ledger.register(path))
        ledger.rollback()
        assert ledger.db.execute('SELECT model FROM active').fetchone()[0] == a.name
        with pytest.raises(PermissionError):
            ledger.activate(b.name, 'PRODUCTION')
        ledger.verify_audit()
    finally:
        ledger.close()


def test_one_human_disposition_and_audit_tamper_detection(tmp_path):
    ledger = Ledger(tmp_path / 'ledger.sqlite')
    try:
        evidence = ledger.record_evidence({'mode':'SHADOW'})
        ledger.review(evidence, 'INVESTIGATE', 'local-reference-reviewer', 'Review sample anomaly')
        with pytest.raises(sqlite3.IntegrityError):
            ledger.review(evidence, 'APPROVE', 'local-reference-reviewer', 'Duplicate decision')
        ledger.verify_audit()
        ledger.db.execute("UPDATE events SET payload='{}' WHERE sequence=1")
        with pytest.raises(ValueError):
            ledger.verify_audit()
    finally:
        ledger.close()


def test_monitoring_reports_shift_and_bad_shape():
    assert monitor_model(model(), np.full((20, 2), 99.))["warning"]
    with pytest.raises(ValueError):
        monitor_model(model(), [[1.]])
    reference = process_baseline(np.linspace(-1, 1, 30))
    assert process_monitor(reference, [0, 10])["three_sigma_indices"] == [1]


def test_retrieval_excludes_future():
    cases = [{"case_id": str(i), "features": [0, 1], "event_time": f"2026-01-0{i}T00:00:00Z"} for i in (1, 3)]
    assert comparable_cases([0, 1], cases, '2026-01-02T00:00:00Z')[0]['case_id'] == '1'


def test_genealogy_requires_evidence_and_rejects_downstream_cycles():
    edges = [{'parent':a,'child':b,'evidence_ref':'fixture'} for a,b in [('a','b'),('b','c')]]
    assert affected_material(edges, 'a')['descendants'] == ['b','c']
    with pytest.raises(ValueError):
        affected_material(edges + [{'parent':'c','child':'b','evidence_ref':'fixture'}], 'a')
    with pytest.raises(ValueError):
        affected_material([{'parent':'a','child':'b'}], 'a')


def test_production_gate_cannot_be_opened_by_self_asserted_flags():
    assert production_gate({})['state'] == 'BLOCKED'
    all_flags = {key: True for key in production_gate({})['missing']}
    assert production_gate(all_flags)['state'] == 'BLOCKED'
