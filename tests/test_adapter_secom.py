from pathlib import Path

from iyqpis.adapters.secom import quality_result_records, telemetry_records
from iyqpis.contracts import validate_batch_strict

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "samples" / "raw" / "secom"
FIXED_INGEST_TIME = "2026-09-28T00:00:00+00:00"


def test_telemetry_sample_validates_and_preserves_missing_as_bad():
    # Full dataset is 1567 rows x 590 sensors; validate a sample for speed, but the missing-value
    # sentinel behavior must hold everywhere a NaN appears.
    sample = []
    saw_missing = False
    for record in telemetry_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME):
        sample.append(record)
        if record["quality_flag"] == "BAD":
            saw_missing = True
        if len(sample) >= 5900:  # first 10 rows
            break
    validate_batch_strict(sample, "telemetry")
    assert saw_missing
    assert all(r["value"] == 0.0 for r in sample if r["quality_flag"] == "BAD")


def test_quality_result_records_validate_and_use_secom_label_convention():
    records = list(quality_result_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    assert len(records) == 1567
    validate_batch_strict(records, "quality_result")
    assert {r["disposition"] for r in records} <= {"PASS", "FAIL"}
    assert any(r["disposition"] == "FAIL" for r in records)
