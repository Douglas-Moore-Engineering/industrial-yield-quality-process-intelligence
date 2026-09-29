"""Data-quality validation library: validates records against the canonical IYQPIS JSON Schema contracts.

See data/contracts/README.md for the contract set and rules.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

from jsonschema import Draft202012Validator, FormatChecker

_CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "data" / "contracts"

_SCHEMA_FILES = {
    "telemetry": "telemetry.schema.json",
    "production_run": "production_run.schema.json",
    "material_lot": "material_lot.schema.json",
    "quality_result": "quality_result.schema.json",
    "maintenance_event": "maintenance_event.schema.json",
    "recommendation": "recommendation.schema.json",
    "decision_outcome": "decision_outcome.schema.json",
}

_validators: dict[str, Draft202012Validator] = {}
_formats = FormatChecker()


@_formats.checks("date-time", raises=(ValueError, OverflowError))
def _valid_timestamp(value: object) -> bool:
    # Enforce the platform's timezone-aware, second-resolution timestamp profile
    # even when jsonschema's optional RFC3339 dependency is not installed.
    if not isinstance(value, str):
        return True
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})", value):
        return False
    return datetime.fromisoformat(value.upper().replace("Z", "+00:00")).tzinfo is not None


class ContractValidationError(ValueError):
    """Raised when one or more records fail contract validation."""

    def __init__(self, contract: str, errors: list[str]) -> None:
        self.contract = contract
        self.errors = errors
        message = f"{len(errors)} record(s) failed '{contract}' validation:\n" + "\n".join(errors)
        super().__init__(message)


def get_validator(contract: str) -> Draft202012Validator:
    """Return a cached Draft 2020-12 validator for the named contract."""
    if contract not in _SCHEMA_FILES:
        raise KeyError(f"Unknown contract '{contract}'. Known contracts: {sorted(_SCHEMA_FILES)}")
    if contract not in _validators:
        schema_path = _CONTRACTS_DIR / _SCHEMA_FILES[contract]
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        _validators[contract] = Draft202012Validator(schema, format_checker=_formats)
    return _validators[contract]


def validate_record(record: dict, contract: str) -> list[str]:
    """Return human-readable validation error strings for a single record; empty list means valid."""
    validator = get_validator(contract)
    return [f"{'.'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in validator.iter_errors(record)]


def validate_batch(records: Iterable[dict], contract: str) -> tuple[list[dict], list[str]]:
    """Validate every record; return (valid_records, error_strings) without raising."""
    valid: list[dict] = []
    errors: list[str] = []
    for i, record in enumerate(records):
        record_errors = validate_record(record, contract)
        if record_errors:
            errors.extend(f"record[{i}]: {e}" for e in record_errors)
        else:
            valid.append(record)
    return valid, errors


def validate_batch_strict(records: Iterable[dict], contract: str) -> list[dict]:
    """Validate every record; raise ContractValidationError listing all failures if any record is invalid."""
    valid, errors = validate_batch(records, contract)
    if errors:
        raise ContractValidationError(contract, errors)
    return valid
