"""CLI: run every dataset adapter, validate its output against contracts, and write one JSONL file per (dataset, contract).

Usage: python -m iyqpis.build_validated <raw-samples-root> <output-dir> [ingest_time_iso]
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from iyqpis.adapters import ai4i_2020, bosch_injector_eol, manufacturing_spc, secom, steel_plates_faults
from iyqpis.contracts import validate_batch_strict

ADAPTERS = {
    "manufacturing-spc": {
        "telemetry": manufacturing_spc.telemetry_records,
        "quality_result": manufacturing_spc.quality_result_records,
    },
    "ai4i-2020-predictive-maintenance": {
        "telemetry": ai4i_2020.telemetry_records,
        "maintenance_event": ai4i_2020.maintenance_event_records,
    },
    "secom": {
        "telemetry": secom.telemetry_records,
        "quality_result": secom.quality_result_records,
    },
    "steel-plates-faults": {
        "telemetry": steel_plates_faults.telemetry_records,
        "quality_result": steel_plates_faults.quality_result_records,
    },
    "bosch-injector-eol": {
        "telemetry": bosch_injector_eol.telemetry_records,
        "quality_result": bosch_injector_eol.quality_result_records,
    },
}


def build(raw_root: Path, output_root: Path, ingest_time: str) -> dict[str, dict[str, int]]:
    """Run every adapter, validate its full output, write one JSONL file per (dataset, contract). Returns counts."""
    counts: dict[str, dict[str, int]] = {}
    for dataset, contracts in ADAPTERS.items():
        dataset_raw_dir = raw_root / dataset
        counts[dataset] = {}
        for contract, record_fn in contracts.items():
            records = list(record_fn(dataset_raw_dir, ingest_time=ingest_time))
            validate_batch_strict(records, contract)
            out_path = output_root / dataset / f"{contract}.jsonl"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record) + "\n")
            counts[dataset][contract] = len(records)
    return counts


def main() -> None:
    raw_root = Path(sys.argv[1])
    output_root = Path(sys.argv[2])
    ingest_time = sys.argv[3] if len(sys.argv) > 3 else datetime.now(timezone.utc).isoformat()
    counts = build(raw_root, output_root, ingest_time)
    for dataset, contract_counts in counts.items():
        for contract, n in contract_counts.items():
            print(f"{dataset}/{contract}: {n} records -> {output_root / dataset / (contract + '.jsonl')}")


if __name__ == "__main__":
    main()
