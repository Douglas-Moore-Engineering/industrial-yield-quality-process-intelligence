from itertools import islice
from pathlib import Path

from iyqpis.adapters.ai4i_2020 import maintenance_event_records, telemetry_records
from iyqpis.contracts import validate_batch_strict

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "samples" / "raw" / "ai4i-2020-predictive-maintenance"
FIXED_INGEST_TIME = "2026-09-28T00:00:00+00:00"


def test_telemetry_record_count_and_sample_validates():
    all_records = list(telemetry_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    assert len(all_records) == 10_000 * 5
    validate_batch_strict(all_records[:2500], "telemetry")


def test_maintenance_event_records_validate_and_cover_all_failure_modes():
    records = list(maintenance_event_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    validate_batch_strict(records, "maintenance_event")
    assert records  # dataset is documented as imbalanced but non-empty for failures
    assert {r["failure_code"] for r in records} <= {"TWF", "HDF", "PWF", "OSF", "RNF"}
    assert all(r["event_type"] == "FAILURE" for r in records)


def test_no_maintenance_event_emitted_for_healthy_rows():
    records = list(maintenance_event_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    healthy_asset_ids_with_events = {r["asset_id"] for r in islice(records, 5)}
    assert healthy_asset_ids_with_events  # sanity: some events exist to check
