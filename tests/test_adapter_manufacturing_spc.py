from pathlib import Path

from iyqpis.adapters.manufacturing_spc import quality_result_records, telemetry_records
from iyqpis.contracts import validate_batch_strict
from iyqpis.timestamps import find_timestamp_anomalies

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "samples" / "raw" / "manufacturing-spc"
FIXED_INGEST_TIME = "2026-09-28T00:00:00+00:00"


def test_telemetry_records_validate_against_contract():
    records = list(telemetry_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    assert len(records) == 2250
    validate_batch_strict(records, "telemetry")


def test_quality_result_records_validate_against_contract():
    records = list(quality_result_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    assert len(records) == 450
    validate_batch_strict(records, "quality_result")


def test_telemetry_timestamps_have_no_integrity_anomalies_per_asset_tag():
    records = list(telemetry_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    # Five measurements share one subgroup timestamp; group by the full genealogy key instead.
    errors = find_timestamp_anomalies(records, group_fields=("asset_id", "tag_id", "sequence_number"))
    assert errors == []


def test_bearing_race_width_drift_flags_final_subgroups_as_failed():
    records = list(quality_result_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    bearing = [r for r in records if r["measurement_name"] == "race width"]
    assert len(bearing) == 90
    # Documented drift: the final subgroups trip a Western Electric rule on 100% of cases.
    assert all(r["disposition"] == "FAIL" for r in bearing[-3:])
    assert any(r["disposition"] == "PASS" for r in bearing[:10])


def test_shaft_diameter_is_mostly_in_control():
    records = list(quality_result_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    shaft = [r for r in records if r["measurement_name"] == "outer diameter"]
    fail_rate = sum(r["disposition"] == "FAIL" for r in shaft) / len(shaft)
    assert fail_rate < 0.05
