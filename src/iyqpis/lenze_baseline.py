"""Training-only feature reference evidence; never changes a frozen model."""
import csv
import hashlib
import json
from pathlib import Path
import argparse
import numpy as np


def build(source: Path, freeze_path: Path) -> dict:
    freeze = json.loads(freeze_path.read_text())
    for name, expected in freeze['sources'].items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Source checksum mismatch')
    with (source / 'Meta_Data.csv').open() as f:
        metadata = list(csv.DictReader(f))
    with (source / 'Original_Features.csv').open() as f:
        records = list(csv.DictReader(f))
    indexed = {r['number']: r for r in records}
    ids = [r['number'] for r in metadata]
    if len(set(ids)) != len(ids) or len(indexed) != len(records) or set(ids) != set(indexed):
        raise ValueError('Identifier contract violated')
    training = [r for r in metadata if r['dataset'] == 'train']
    if not training or any(r['class_label'] != 'normal' for r in training):
        raise ValueError('Invalid normal reference population')
    names = freeze['features']
    x = np.array([[float(indexed[r['number']][k]) for k in names] for r in training])
    if not np.isfinite(x).all():
        raise ValueError('Feature finiteness contract violated')
    profile = {}
    for i, name in enumerate(names):
        v = x[:, i]
        profile[name] = dict(count=len(v), mean=float(v.mean()), std=float(v.std()),
                             minimum=float(v.min()), maximum=float(v.max()),
                             quantiles=dict(zip(['p01','p05','p50','p95','p99'],
                                                map(float, np.quantile(v,[.01,.05,.5,.95,.99])))))
    return dict(version=1, scope='retrospective reference evidence; not production approval',
                population='publisher training only; all normal, including calibration rows',
                training_rows=len(training), variants=len({r['A_Variant_ID'] for r in training}),
                source_sha256=freeze['sources'], frozen_model_sha256=freeze['model_sha256'],
                features=profile, missing_cells=0, nonfinite_cells=0,
                duplicate_feature_rows=len(x)-len(np.unique(x,axis=0)),
                test_used=False, process_control_limits='unavailable: raw process history absent',
                freshness='unverified: event timestamps absent',
                point_in_time='unverified: upstream extraction history unavailable',
                thresholds_changed=False, owner='reference engineering role', approver='unassigned')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('freeze',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args(); result=build(a.source,a.freeze)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x') as f: json.dump(result,f,indent=2);f.write('\n')
