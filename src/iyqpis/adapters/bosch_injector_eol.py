"""Adapter: Bosch fuel-injector EoL raw CSV -> validated telemetry + quality_result records.

Source: data/samples/raw/bosch-injector-eol (Robert Bosch GmbH / SoliDAIR, CC BY-NC-ND 4.0).
Feature names are provider-obfuscated and no timestamp, asset ID, or pass/fail threshold exists
in the source, so event_time/asset_id are synthesized (declared, not real) and disposition is
UNKNOWN -- the source description states only that EoL output values are a regression target,
not a defined pass/fail rule. Do not fabricate a threshold; that requires data-owner review.
A small fraction of input/output cells are empty in the source; telemetry preserves these as
quality_flag=BAD with a documented value=0.0 sentinel, and quality_result leaves measurement_value
null, rather than dropping the observation.
"""
from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

SOURCE_SYSTEM = "sample:bosch-injector-eol"
PLANT_ID = "sample-plant-01"
SCHEMA_VERSION = "1.0.0"
_SYNTHETIC_BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)
_INPUT_COUNT = 67
_OUTPUT_COUNT = 4
_MISSING_VALUE_SENTINEL = 0.0


def _read_csv(path: Path) -> Iterator[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f)


def telemetry_records(raw_dir: Path, ingest_time: str | None = None) -> Iterator[dict]:
    """Yield one telemetry record per (part, obfuscated process input); sparse missing readings are BAD, not dropped."""
    ingest_time = ingest_time or datetime.now(timezone.utc).isoformat()
    for i, row in enumerate(_read_csv(raw_dir / "anonymized_data.csv")):
        event_time = (_SYNTHETIC_BASE + timedelta(seconds=i)).isoformat()
        asset_id = f"bosch-injector-{i}"
        for k in range(1, _INPUT_COUNT + 1):
            raw_value = row[f"Input_{k}"]
            missing = raw_value == ""
            yield {
                "schema_version": SCHEMA_VERSION,
                "event_id": f"bosch-injector-{i}-input-{k}",
                "event_time": event_time,
                "ingest_time": ingest_time,
                "source_system": SOURCE_SYSTEM,
                "plant_id": PLANT_ID,
                "line_id": None,
                "asset_id": asset_id,
                "tag_id": f"input_{k}",
                "engineering_unit": "unitless",
                "value": _MISSING_VALUE_SENTINEL if missing else float(raw_value),
                "quality_flag": "BAD" if missing else "GOOD",
                "sequence_number": i,
            }


def quality_result_records(raw_dir: Path, ingest_time: str | None = None) -> Iterator[dict]:
    """Yield one quality_result record per (part, EoL output); disposition is UNKNOWN (no defined threshold)."""
    ingest_time = ingest_time or datetime.now(timezone.utc).isoformat()
    for i, row in enumerate(_read_csv(raw_dir / "anonymized_data.csv")):
        event_time = (_SYNTHETIC_BASE + timedelta(seconds=i)).isoformat()
        for k in range(1, _OUTPUT_COUNT + 1):
            raw_value = row[f"Output_{k}"]
            yield {
                "schema_version": SCHEMA_VERSION,
                "event_id": f"bosch-injector-{i}-output-{k}",
                "event_time": event_time,
                "ingest_time": ingest_time,
                "source_system": SOURCE_SYSTEM,
                "plant_id": PLANT_ID,
                "line_id": None,
                "quality_result_id": f"bosch-injector-{i}-output-{k}",
                "run_id": None,
                "material_lot_id": None,
                "product_instance_id": f"bosch-injector-{i}",
                "measurement_name": f"eol_output_{k}",
                "measurement_value": None if raw_value == "" else float(raw_value),
                "engineering_unit": None,
                "lower_spec_limit": None,
                "upper_spec_limit": None,
                "method_id": "bosch-eol-test",
                "disposition": "UNKNOWN",
            }
