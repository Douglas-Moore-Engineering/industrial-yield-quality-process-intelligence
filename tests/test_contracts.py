from copy import deepcopy

import pytest

from iyqpis.contracts import ContractValidationError, validate_batch, validate_batch_strict, validate_record

VALID_TELEMETRY = {
    "schema_version": "1.0.0",
    "event_id": "evt-1",
    "event_time": "2026-01-01T00:00:00+00:00",
    "ingest_time": "2026-01-01T00:00:05+00:00",
    "source_system": "test",
    "plant_id": "plant-1",
    "line_id": None,
    "asset_id": "asset-1",
    "tag_id": "tag-1",
    "engineering_unit": "mm",
    "value": 1.23,
    "quality_flag": "GOOD",
    "sequence_number": 1,
}


def test_valid_telemetry_record_passes():
    assert validate_record(VALID_TELEMETRY, "telemetry") == []


def test_missing_required_field_fails():
    record = deepcopy(VALID_TELEMETRY)
    del record["asset_id"]
    errors = validate_record(record, "telemetry")
    assert errors
    assert any("asset_id" in e for e in errors)


def test_additional_property_rejected():
    record = deepcopy(VALID_TELEMETRY)
    record["unexpected_field"] = "x"
    assert validate_record(record, "telemetry") != []


def test_wrong_quality_flag_enum_rejected():
    record = deepcopy(VALID_TELEMETRY)
    record["quality_flag"] = "FINE"
    assert validate_record(record, "telemetry") != []


def test_unknown_contract_raises_keyerror():
    with pytest.raises(KeyError):
        validate_record({}, "not_a_contract")


def test_validate_batch_separates_valid_and_invalid():
    bad = {"schema_version": "1.0.0"}
    valid, errors = validate_batch([VALID_TELEMETRY, bad], "telemetry")
    assert valid == [VALID_TELEMETRY]
    assert errors
    assert all("record[1]" in e for e in errors)


def test_validate_batch_strict_raises_on_any_invalid():
    bad = {"schema_version": "1.0.0"}
    with pytest.raises(ContractValidationError):
        validate_batch_strict([VALID_TELEMETRY, bad], "telemetry")


def test_validate_batch_strict_returns_records_when_all_valid():
    result = validate_batch_strict([VALID_TELEMETRY], "telemetry")
    assert result == [VALID_TELEMETRY]
