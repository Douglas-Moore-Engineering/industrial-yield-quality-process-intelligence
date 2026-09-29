"""Replayable sample-data batch pipeline; complete manifests are the publication boundary.

Never changes raw inputs. Does not infer missing manufacturing genealogy or train models.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import sqlite3
import tempfile

from iyqpis.build_validated import ADAPTERS
from iyqpis.contracts import validate_record


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def utc_time(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("ingest time must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat()


def verify_run(run: Path) -> dict:
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "complete" or manifest.get("run_id") != run.name:
        raise ValueError("Run is not complete or its identity does not match")
    for artifact in manifest["artifacts"]:
        path = (run / artifact["path"]).resolve()
        if not path.is_relative_to(run.resolve()) or not path.is_file() or digest(path) != artifact["sha256"]:
            raise ValueError("Run artifact missing, outside run, or checksum mismatch")
    return manifest


def build_run(raw_root: Path, output_root: Path, ingest_time: str, datasets=None) -> Path:
    raw_root, output_root = raw_root.resolve(), output_root.resolve()
    if output_root == raw_root or output_root.is_relative_to(raw_root):
        raise ValueError("Output must be outside the immutable raw root")
    selected = sorted(set(datasets if datasets is not None else ADAPTERS))
    if not selected or any(name not in ADAPTERS for name in selected):
        raise ValueError("Choose known, nonempty dataset names")
    ingest_time = utc_time(ingest_time)
    sources = []
    for name in selected:
        files = sorted((raw_root / name).rglob("*"))
        if not any(path.is_file() for path in files):
            raise ValueError(f"Missing raw dataset: {name}")
        for path in files:
            if path.is_file():
                if path.is_symlink() or not path.resolve().is_relative_to(raw_root):
                    raise ValueError("Raw inputs must not escape the raw root")
                sources.append({"path": path.relative_to(raw_root).as_posix(), "sha256": digest(path)})
    package = Path(__file__).parent
    schemas = package.parents[1] / "data" / "contracts"
    implementation = {p.relative_to(package).as_posix(): digest(p) for p in sorted(package.rglob("*.py"))}
    contracts = {p.name: digest(p) for p in sorted(schemas.glob("*.schema.json"))}
    identity = {"sources": sources, "implementation": implementation, "contracts": contracts,
                "ingest_time": ingest_time, "datasets": selected, "pipeline_version": 1}
    run_id = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:32]
    output_root.mkdir(parents=True, exist_ok=True)
    destination = output_root / run_id
    if destination.exists():
        verify_run(destination)
        return destination
    stage = Path(tempfile.mkdtemp(prefix=".pending-", dir=output_root))
    database = sqlite3.connect(stage / "events.sqlite")
    database.execute("CREATE TABLE events (dataset TEXT, event_id TEXT, PRIMARY KEY(dataset,event_id))")
    artifacts, metrics = [], {}
    try:
        for dataset in selected:
            for contract, adapter in ADAPTERS[dataset].items():
                relative = f"validated/{dataset}/{contract}.jsonl"
                path = stage / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                count, flags, dispositions = 0, Counter(), Counter()
                streams, groups = {}, {}
                with path.open("w", encoding="utf-8", newline="\n") as target:
                    for record in adapter(raw_root / dataset, ingest_time=ingest_time):
                        errors = validate_record(record, contract)
                        if errors:
                            raise ValueError(f"{dataset}/{contract} record {count}: {errors[0]}")
                        # Event IDs are unique within a dataset, including across contract types.
                        database.execute("INSERT INTO events VALUES (?, ?)", (dataset, record["event_id"]))
                        serialized = json.dumps(record, sort_keys=True, allow_nan=False)
                        target.write(serialized + "\n")
                        count += 1
                        if contract == "telemetry":
                            flag = record["quality_flag"]
                            flags[flag] += 1
                            key = (record["asset_id"], record["tag_id"], record["engineering_unit"])
                            at = datetime.fromisoformat(record["event_time"].replace("Z", "+00:00"))
                            summary = groups.setdefault(key, {"records": 0, "good_records": 0, "sum": 0.0,
                                                               "min": None, "max": None, "out_of_order": 0})
                            summary["records"] += 1
                            if key in streams and at < streams[key]:
                                summary["out_of_order"] += 1
                            streams[key] = max(streams.get(key, at), at)
                            if flag == "GOOD":
                                value = record["value"]
                                if not math.isfinite(value):
                                    raise ValueError("Non-finite measurement")
                                summary["good_records"] += 1
                                summary["sum"] += value
                                summary["min"] = value if summary["min"] is None else min(summary["min"], value)
                                summary["max"] = value if summary["max"] is None else max(summary["max"], value)
                        elif contract == "quality_result":
                            dispositions[record["disposition"]] += 1
                artifacts.append({"path": relative, "sha256": digest(path), "records": count, "bytes": path.stat().st_size})
                metrics[f"{dataset}/{contract}"] = {"records": count, "quality_flags": dict(flags),
                                                    "dispositions": dict(dispositions)}
                if contract == "telemetry":
                    summary_path = stage / f"contextualized/{dataset}/stream-summary.jsonl"
                    summary_path.parent.mkdir(parents=True, exist_ok=True)
                    with summary_path.open("w", encoding="utf-8", newline="\n") as target:
                        for key, summary in sorted(groups.items()):
                            good = summary["good_records"]
                            summary["mean"] = summary.pop("sum") / good if good else None
                            target.write(json.dumps({"asset_id": key[0], "tag_id": key[1], "engineering_unit": key[2],
                                                     **summary}, sort_keys=True, allow_nan=False) + "\n")
                    artifacts.append({"path": summary_path.relative_to(stage).as_posix(), "sha256": digest(summary_path),
                                      "records": len(groups), "bytes": summary_path.stat().st_size})
        # Prevent a changing source directory from producing a falsely attributed run.
        for source in sources:
            if digest(raw_root / source["path"]) != source["sha256"]:
                raise ValueError("Raw source changed during the run")
        report = stage / "curated-evidence/quality-report.json"
        write_json(report, {"run_id": run_id, "metrics": metrics,
                           "scope": "sample-data batch; no inferred genealogy or production acceptance",
                           "ordering": "historical out-of-order records reported; distinct events at equal times retained",
                           "missing_values": "BAD/UNCERTAIN retained in validated zone, excluded from GOOD aggregates",
                           "timestamp_provenance": "See source adapters: synthetic or assumed UTC where declared"})
        artifacts.append({"path": "curated-evidence/quality-report.json", "sha256": digest(report), "bytes": report.stat().st_size})
        database.close()
        (stage / "events.sqlite").unlink()
        write_json(stage / "manifest.json", {"run_id": run_id, "status": "complete", **identity, "artifacts": artifacts})
        try:
            stage.rename(destination)
        except OSError:
            if not destination.exists():
                raise
            verify_run(destination)
            shutil.rmtree(stage)
        return destination
    except Exception as error:
        database.close()
        # Keep failed evidence quarantined locally; no completion marker is published.
        write_json(stage / "failure.json", {"status": "failed", "run_id": run_id, "error_type": type(error).__name__})
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_root", type=Path)
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--ingest-time", required=True, help="Fixed timezone-aware timestamp, reused for replay")
    parser.add_argument("--dataset", action="append", choices=sorted(ADAPTERS))
    args = parser.parse_args()
    path = build_run(args.raw_root, args.output_root, args.ingest_time, args.dataset)
    manifest = verify_run(path)
    print(json.dumps({"run_id": path.name, "status": manifest["status"], "artifacts": len(manifest["artifacts"])}))


if __name__ == "__main__":
    main()
