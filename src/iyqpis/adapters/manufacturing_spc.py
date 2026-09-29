"""Adapter: manufacturing-spc raw CSVs -> validated telemetry + quality_result records.

Source: data/samples/raw/manufacturing-spc (CC0, Misata). Genealogy: measurement -> subgroup -> process.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

SOURCE_SYSTEM = "sample:manufacturing-spc"
PLANT_ID = "sample-plant-01"
SCHEMA_VERSION = "1.0.0"


def _read_csv(path: Path) -> Iterator[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f)


def _iso(timestamp: str) -> str:
    # Subgroup timestamps are naive "YYYY-MM-DD HH:MM:SS"; declared as UTC per source generation.
    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).isoformat()


def load_processes(raw_dir: Path) -> dict[str, dict[str, str]]:
    return {row["process_id"]: row for row in _read_csv(raw_dir / "processes.csv")}


def load_subgroup_timestamps(raw_dir: Path) -> dict[str, str]:
    return {row["subgroup_id"]: row["timestamp"] for row in _read_csv(raw_dir / "subgroups.csv")}


def telemetry_records(raw_dir: Path, ingest_time: str | None = None) -> Iterator[dict]:
    """Yield one telemetry record per individual measurement."""
    processes = load_processes(raw_dir)
    subgroup_ts = load_subgroup_timestamps(raw_dir)
    ingest_time = ingest_time or datetime.now(timezone.utc).isoformat()
    for row in _read_csv(raw_dir / "measurements.csv"):
        process = processes[row["process_id"]]
        yield {
            "schema_version": SCHEMA_VERSION,
            "event_id": f"manufacturing-spc-measurement-{row['measurement_id']}",
            "event_time": _iso(subgroup_ts[row["subgroup_id"]]),
            "ingest_time": ingest_time,
            "source_system": SOURCE_SYSTEM,
            "plant_id": PLANT_ID,
            "line_id": None,
            "asset_id": f"process-{row['process_id']}",
            "tag_id": process["characteristic"],
            "engineering_unit": process["unit"],
            "value": float(row["value"]),
            "quality_flag": "GOOD",
            "sequence_number": int(row["sample_index"]),
        }


def quality_result_records(raw_dir: Path, ingest_time: str | None = None) -> Iterator[dict]:
    """Yield one quality_result record per Xbar-R subgroup, disposed by the Western Electric rule flags."""
    processes = load_processes(raw_dir)
    ingest_time = ingest_time or datetime.now(timezone.utc).isoformat()
    for row in _read_csv(raw_dir / "subgroups.csv"):
        process = processes[row["process_id"]]
        out_of_control = row["out_of_control"].strip().lower() == "true"
        yield {
            "schema_version": SCHEMA_VERSION,
            "event_id": f"manufacturing-spc-subgroup-{row['subgroup_id']}",
            "event_time": _iso(row["timestamp"]),
            "ingest_time": ingest_time,
            "source_system": SOURCE_SYSTEM,
            "plant_id": PLANT_ID,
            "line_id": None,
            "quality_result_id": f"subgroup-{row['subgroup_id']}",
            "run_id": None,
            "material_lot_id": None,
            "product_instance_id": None,
            "measurement_name": process["characteristic"],
            "measurement_value": float(row["xbar"]),
            "engineering_unit": process["unit"],
            "lower_spec_limit": float(process["lsl"]),
            "upper_spec_limit": float(process["usl"]),
            "method_id": "xbar-r-control-chart",
            "disposition": "FAIL" if out_of_control else "PASS",
        }
