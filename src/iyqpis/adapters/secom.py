"""Adapter: SECOM raw sensor/label files -> validated telemetry + quality_result records.

Source: data/samples/raw/secom (UCI ML Repository). secom_labels.data carries a real per-row
timestamp (dd/mm/yyyy HH:MM:SS, declared UTC since the source has no timezone). Missing sensor
readings ("NaN") are preserved as quality_flag=BAD with a documented value=0.0 sentinel, since the
telemetry contract's `value` is a required non-nullable number -- the reading is recorded as having
occurred and failed, not silently dropped.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

SOURCE_SYSTEM = "sample:secom"
PLANT_ID = "sample-plant-01"
ASSET_ID = "secom-line-01"
SCHEMA_VERSION = "1.0.0"
_MISSING_VALUE_SENTINEL = 0.0


def _read_labels(raw_dir: Path) -> Iterator[tuple[int, str]]:
    with (raw_dir / "secom_labels.data").open(encoding="utf-8") as f:
        for line in f:
            label_str, ts_str = line.strip().split(maxsplit=1)
            ts = datetime.strptime(ts_str.strip('"'), "%d/%m/%Y %H:%M:%S").replace(tzinfo=timezone.utc)
            yield int(label_str), ts.isoformat()


def _read_rows(raw_dir: Path) -> Iterator[list[str]]:
    with (raw_dir / "secom.data").open(encoding="utf-8") as f:
        for line in f:
            yield line.split()


def telemetry_records(raw_dir: Path, ingest_time: str | None = None) -> Iterator[dict]:
    """Yield one telemetry record per (row, sensor) pair; missing readings are BAD, not dropped."""
    ingest_time = ingest_time or datetime.now(timezone.utc).isoformat()
    labels = list(_read_labels(raw_dir))
    for i, (row, (_label, event_time)) in enumerate(zip(_read_rows(raw_dir), labels)):
        for j, raw_value in enumerate(row, start=1):
            missing = raw_value == "NaN"
            yield {
                "schema_version": SCHEMA_VERSION,
                "event_id": f"secom-{i}-sensor-{j}",
                "event_time": event_time,
                "ingest_time": ingest_time,
                "source_system": SOURCE_SYSTEM,
                "plant_id": PLANT_ID,
                "line_id": None,
                "asset_id": ASSET_ID,
                "tag_id": f"sensor_{j}",
                "engineering_unit": "unitless",
                "value": _MISSING_VALUE_SENTINEL if missing else float(raw_value),
                "quality_flag": "BAD" if missing else "GOOD",
                "sequence_number": i,
            }


def quality_result_records(raw_dir: Path, ingest_time: str | None = None) -> Iterator[dict]:
    """Yield one quality_result record per row; SECOM convention: label -1 = pass, 1 = fail."""
    ingest_time = ingest_time or datetime.now(timezone.utc).isoformat()
    for i, (label, event_time) in enumerate(_read_labels(raw_dir)):
        yield {
            "schema_version": SCHEMA_VERSION,
            "event_id": f"secom-{i}-result",
            "event_time": event_time,
            "ingest_time": ingest_time,
            "source_system": SOURCE_SYSTEM,
            "plant_id": PLANT_ID,
            "line_id": None,
            "quality_result_id": f"secom-{i}",
            "run_id": None,
            "material_lot_id": None,
            "product_instance_id": None,
            "measurement_name": "secom-pass-fail",
            "measurement_value": None,
            "engineering_unit": None,
            "lower_spec_limit": None,
            "upper_spec_limit": None,
            "method_id": "secom-eol-test",
            "disposition": "FAIL" if label == 1 else "PASS",
        }
