from pathlib import Path

from iyqpis.adapters.bosch_injector_eol import quality_result_records, telemetry_records
from iyqpis.contracts import validate_batch_strict

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "samples" / "raw" / "bosch-injector-eol"
FIXED_INGEST_TIME = "2026-09-28T00:00:00+00:00"


def test_telemetry_record_count_and_sample_validates():
    all_records = list(telemetry_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    assert len(all_records) == 1000 * 67
    validate_batch_strict(all_records[:2680], "telemetry")


def test_quality_result_records_validate_and_are_unknown_disposition():
    records = list(quality_result_records(RAW_DIR, ingest_time=FIXED_INGEST_TIME))
    assert len(records) == 1000 * 4
    validate_batch_strict(records[:400], "quality_result")
    # No pass/fail threshold is defined by the source; fabricating one requires data-owner review.
    assert all(r["disposition"] == "UNKNOWN" for r in records)
