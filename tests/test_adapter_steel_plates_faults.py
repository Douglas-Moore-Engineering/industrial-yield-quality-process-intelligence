from pathlib import Path

from iyqpis.adapters.steel_plates_faults import quality_result_records, telemetry_records
from iyqpis.contracts import validate_batch_strict

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "samples" / "raw" / "steel-plates-faults"
FIXED_INGEST_TIME = "2026-09-28T00:00:00+00:00"
FAULT_NAMES = {"Pastry", "Z_Scratch", "K_Scatch", "Stains", "Dirtiness", "Bumps", "Other_Faults"}


def test_telemetry_sample_validates():
    sample = []
    for record in telemetry_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME):
        sample.append(record)
        if len(sample) >= 2700:  # first 100 plates (27 features each)
            break
    validate_batch_strict(sample, "telemetry")


def test_quality_result_records_validate_and_are_all_fail_with_known_fault_names():
    records = list(quality_result_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    assert len(records) == 1941
    validate_batch_strict(records, "quality_result")
    assert all(r["disposition"] == "FAIL" for r in records)
    assert {r["measurement_name"] for r in records} <= FAULT_NAMES
