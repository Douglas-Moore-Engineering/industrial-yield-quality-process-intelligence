"""Exercise the advisory software sequence with explicitly marked reference evidence."""
import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

from iyqpis.intelligence import infer, load_features, temporal_partitions, verify_bundle
from iyqpis.operations import (Ledger, affected_material, comparable_cases, monitor_model,
                               process_baseline, process_monitor, production_gate)
from iyqpis.pipeline import write_json


def validate_reference(data_run: Path, bundle: Path, output: Path):
    model = verify_bundle(bundle)
    x, y, times, keys, source = load_features(data_run)
    train, calibration, test = temporal_partitions(times)
    at = datetime.fromisoformat(times[test[0]])
    row = {name: None if np.isnan(value) else float(value) for name, value in zip(model["features"], x[test[0]])}
    shadow = infer(model, row, times[test[0]], "sample:secom", now=at)
    stale = infer(model, row, times[test[0]], "sample:secom", now=at + timedelta(hours=1))
    wrong_domain = infer(model, row, times[test[0]], "unapproved:plant", now=at)
    output.mkdir(parents=True, exist_ok=True)
    ledger_path = output / "reference-ledger.sqlite"
    if ledger_path.exists():
        raise ValueError("Reference validation requires a fresh output directory")
    ledger = Ledger(ledger_path)
    try:
        registered = ledger.register(bundle)
        ledger.activate(registered)
        evidence_id = ledger.record_evidence(shadow)
        ledger.review(evidence_id, "INVESTIGATE", "reference-reviewer", "Synthetic review exercise; no plant action")
        audit = ledger.verify_audit()
        try:
            ledger.activate(registered, "PRODUCTION")
        except PermissionError:
            production_refused = True
        else:
            raise AssertionError("Production activation was not refused")
    finally:
        ledger.close()
    # Explicit synthetic fixtures: no inferred customer lots or manufacturing limits.
    baseline = process_baseline(np.linspace(-1, 1, 30))
    excursion = process_monitor(baseline, [0., .1, 5.])
    genealogy = affected_material([
        {"parent": "reference-lot", "child": "reference-spool", "evidence_ref": "synthetic-fixture"},
        {"parent": "reference-spool", "child": "reference-product", "evidence_ref": "synthetic-fixture"}], "reference-lot")
    retrieval = comparable_cases([0., 1.], [
        {"case_id": "past-fixture", "event_time": "2026-01-01T00:00:00Z", "features": [0., 1.]},
        {"case_id": "future-fixture", "event_time": "2026-01-03T00:00:00Z", "features": [0., 1.]}],
        "2026-01-02T00:00:00Z")
    report = {"scope": "reference industrial manufacturing validation; no customer facility",
              "model_id": registered, "data_run_id": source["run_id"], "shadow_example": shadow,
              "stale_abstains": stale["shadow_probability"] is None,
              "unknown_domain_abstains": wrong_domain["shadow_probability"] is None,
              "production_activation_refused": production_refused,
              "audit_chain_sha256": audit, "review": "INVESTIGATE; simulated local reviewer",
              "monitoring": monitor_model(model, x[test], y[test]),
              "spc_fixture": excursion, "genealogy_fixture": genealogy, "retrieval_fixture": retrieval,
              "production_gate": production_gate({}),
              "disabled_capabilities": ["Plant control writes", "Causal intervention claims", "Digital twin prescription",
                                        "Unapproved yield/scrap estimates", "Agent autonomy", "Production promotion"],
              "authentication_scope": "local operator only; no multi-user production service"}
    if not report["stale_abstains"] or not report["unknown_domain_abstains"] or excursion["three_sigma_indices"] != [2]:
        raise AssertionError("Reference safety validation failed")
    write_json(output / "reference-validation.json", report)
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_run", type=Path)
    parser.add_argument("model_bundle", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = validate_reference(args.data_run, args.model_bundle, args.output)
    print(json.dumps({"status": "complete", "model_id": result["model_id"],
                      "production_release": result["production_gate"]["state"]}))
