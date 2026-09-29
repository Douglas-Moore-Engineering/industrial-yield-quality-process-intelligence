"""Audit the source encoding and reserve setting groups without reading outcomes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


def audit(payload: bytes) -> dict:
    rows = list(csv.reader(io.StringIO(payload.decode('utf-8-sig')), delimiter=';'))
    if len(rows) < 6 or [r[0].strip() for r in rows[:4]] != [
        '6', 'AcelR fz Diam ae HB geom', '1', 'Ra'
    ]:
        raise ValueError('Unexpected milling source preamble')
    observations = rows[5:]
    if len(observations) != int(rows[4][0]) or any(len(r) != 7 for r in observations):
        raise ValueError('Row count or width mismatch')
    assignments = []
    groups: dict[str, str] = {}
    ambiguous = 0
    for row in observations:
        # Raw setting fields only: exclude measured vibration and target Ra.
        key = json.dumps(row[1:6], separators=(',', ':'))
        digest = hashlib.sha256(('milling-settings-v1:' + key).encode()).hexdigest()
        bucket = int(digest[:8], 16) % 10
        split = 'test' if bucket < 2 else 'validation' if bucket < 4 else 'train'
        groups[digest] = split
        assignments.append(digest)
        ambiguous += sum(value.count('.') > 1 for value in row[:6])
    return {
        'source_sha256': hashlib.sha256(payload).hexdigest(),
        'rows': len(observations), 'setting_groups': len(groups),
        'split_rule': 'SHA256 raw settings, fixed salt v1; buckets 0-1 test, 2-3 validation, 4-9 train',
        'groups': groups, 'row_groups': assignments,
        'split_rows': {s: sum(groups[g] == s for g in assignments)
                       for s in ('train', 'validation', 'test')},
        'ambiguous_input_cells': ambiguous,
        'numeric_encoding': 'unresolved; no numeric coercion performed',
        'outcomes_evaluated': False,
        'limitation': 'Setting groups are not verified independent parts or production runs',
        'training_ready': False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = audit(args.source.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Preserve the first split reservation; never silently overwrite it.
    with args.output.open('x', encoding='utf-8') as out:
        json.dump(result, out, indent=2)
        out.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k not in {'groups', 'row_groups'}}))


if __name__ == '__main__':
    main()
