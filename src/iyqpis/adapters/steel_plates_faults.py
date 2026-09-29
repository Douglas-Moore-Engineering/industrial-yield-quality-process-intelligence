"""Adapter: Steel Plates Faults raw files -> validated telemetry + quality_result records.

Source: data/samples/raw/steel-plates-faults (UCI ML Repository). No timestamp or asset ID exists
in the source; event_time is synthesized as a sequential ordering (declared, not real wall-clock)
and asset_id is a synthetic per-plate identifier. Every row in this dataset is a faulty plate
(fault-type classification only, no passing plates), so disposition is always FAIL.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

SOURCE_SYSTEM = "sample:steel-plates-faults"
PLANT_ID = "sample-plant-01"
SCHEMA_VERSION = "1.0.0"
_SYNTHETIC_BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)
_FEATURE_COUNT = 27


def _load_columns(raw_dir: Path) -> list[str]:
    return [line.strip() for line in (raw_dir / "Faults27x7_var").read_text(encoding="utf-8").splitlines() if line.strip()]


def _read_rows(raw_dir: Path) -> Iterator[list[str]]:
    with (raw_dir / "Faults.NNA").open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield line.split()


def telemetry_records(raw_dir: Path, ingest_time: str | None = None) -> Iterator[dict]:
    """Yield one telemetry record per (plate, geometry/luminosity feature)."""
    columns = _load_columns(raw_dir)
    feature_names = columns[:_FEATURE_COUNT]
    ingest_time = ingest_time or datetime.now(timezone.utc).isoformat()
    for i, row in enumerate(_read_rows(raw_dir)):
        event_time = (_SYNTHETIC_BASE + timedelta(seconds=i)).isoformat()
        asset_id = f"steel-plate-{i}"
        for name, value in zip(feature_names, row[:_FEATURE_COUNT]):
            yield {
                "schema_version": SCHEMA_VERSION,
                "event_id": f"steel-plate-{i}-{name}",
                "event_time": event_time,
                "ingest_time": ingest_time,
                "source_system": SOURCE_SYSTEM,
                "plant_id": PLANT_ID,
                "line_id": None,
                "asset_id": asset_id,
                "tag_id": name,
                "engineering_unit": "unitless",
                "value": float(value),
                "quality_flag": "GOOD",
                "sequence_number": i,
            }


def quality_result_records(raw_dir: Path, ingest_time: str | None = None) -> Iterator[dict]:
    """Yield one quality_result record per plate, naming whichever one-hot fault column fired."""
    columns = _load_columns(raw_dir)
    fault_names = columns[_FEATURE_COUNT:]
    ingest_time = ingest_time or datetime.now(timezone.utc).isoformat()
    for i, row in enumerate(_read_rows(raw_dir)):
        event_time = (_SYNTHETIC_BASE + timedelta(seconds=i)).isoformat()
        fault_flags = row[_FEATURE_COUNT:]
        fired = [name for name, flag in zip(fault_names, fault_flags) if flag == "1"]
        fault_name = fired[0] if fired else "unclassified"
        yield {
            "schema_version": SCHEMA_VERSION,
            "event_id": f"steel-plate-{i}-result",
            "event_time": event_time,
            "ingest_time": ingest_time,
            "source_system": SOURCE_SYSTEM,
            "plant_id": PLANT_ID,
            "line_id": None,
            "quality_result_id": f"steel-plate-{i}",
            "run_id": None,
            "material_lot_id": None,
            "product_instance_id": f"steel-plate-{i}",
            "measurement_name": fault_name,
            "measurement_value": None,
            "engineering_unit": None,
            "lower_spec_limit": None,
            "upper_spec_limit": None,
            "method_id": "steel-plate-visual-inspection",
            "disposition": "FAIL",
        }
