"""Adapter: AI4I 2020 Predictive Maintenance raw CSV -> validated telemetry + maintenance_event records.

Source: data/samples/raw/ai4i-2020-predictive-maintenance (UCI ML Repository).
No wall-clock timestamp exists in the source; event_time is synthesized from the UDI sequence
(one synthetic minute per unit) and is declared ordering, not a real timestamp.
"""
from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

SOURCE_SYSTEM = "sample:ai4i-2020-predictive-maintenance"
PLANT_ID = "sample-plant-01"
SCHEMA_VERSION = "1.0.0"
_SYNTHETIC_BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)

_TAGS = [
    ("Air temperature [K]", "air_temperature", "K"),
    ("Process temperature [K]", "process_temperature", "K"),
    ("Rotational speed [rpm]", "rotational_speed", "rpm"),
    ("Torque [Nm]", "torque", "Nm"),
    ("Tool wear [min]", "tool_wear", "min"),
]
_FAILURE_MODES = ["TWF", "HDF", "PWF", "OSF", "RNF"]


def _read_csv(path: Path) -> Iterator[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        yield from csv.DictReader(f)


def _synthetic_event_time(udi: int) -> str:
    return (_SYNTHETIC_BASE + timedelta(minutes=udi)).isoformat()


def telemetry_records(raw_dir: Path, ingest_time: str | None = None) -> Iterator[dict]:
    """Yield one telemetry record per (row, process measurement)."""
    ingest_time = ingest_time or datetime.now(timezone.utc).isoformat()
    for row in _read_csv(raw_dir / "ai4i2020.csv"):
        udi = int(row["UDI"])
        event_time = _synthetic_event_time(udi)
        asset_id = f"product-{row['Product ID']}"
        for column, tag_id, unit in _TAGS:
            yield {
                "schema_version": SCHEMA_VERSION,
                "event_id": f"ai4i2020-{udi}-{tag_id}",
                "event_time": event_time,
                "ingest_time": ingest_time,
                "source_system": SOURCE_SYSTEM,
                "plant_id": PLANT_ID,
                "line_id": None,
                "asset_id": asset_id,
                "tag_id": tag_id,
                "engineering_unit": unit,
                "value": float(row[column]),
                "quality_flag": "GOOD",
                "sequence_number": udi,
            }


def maintenance_event_records(raw_dir: Path, ingest_time: str | None = None) -> Iterator[dict]:
    """Yield one maintenance_event per triggered failure mode (rows with no failure yield nothing)."""
    ingest_time = ingest_time or datetime.now(timezone.utc).isoformat()
    for row in _read_csv(raw_dir / "ai4i2020.csv"):
        if row["Machine failure"] != "1":
            continue
        udi = int(row["UDI"])
        event_time = _synthetic_event_time(udi)
        asset_id = f"product-{row['Product ID']}"
        for mode in _FAILURE_MODES:
            if row[mode] != "1":
                continue
            yield {
                "schema_version": SCHEMA_VERSION,
                "event_id": f"ai4i2020-{udi}-failure-{mode}",
                "event_time": event_time,
                "ingest_time": ingest_time,
                "source_system": SOURCE_SYSTEM,
                "plant_id": PLANT_ID,
                "line_id": None,
                "maintenance_event_id": f"ai4i2020-{udi}-{mode}",
                "asset_id": asset_id,
                "component_id": None,
                "work_order_id": None,
                "event_type": "FAILURE",
                "failure_code": mode,
                "completion_time": None,
                "notes_ref": None,
            }
