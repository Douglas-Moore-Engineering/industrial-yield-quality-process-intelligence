"""Per-record verification of an existing trusted frozen benchmark."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np


def decision_digest(ids, scores, cutoff):
    values = np.asarray(scores, dtype=float)
    if values.ndim != 1 or len(ids) != len(values) or not len(ids):
        raise ValueError('Invalid prediction shape')
    if len(set(ids)) != len(ids) or not np.isfinite(values).all() or not np.isfinite(cutoff):
        raise ValueError('Invalid identifiers or scores')
    records = sorted(zip(ids, (values > cutoff).tolist()))
    return hashlib.sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest()


def verify(root, expected_freeze_sha256):
    raw = (root / 'freeze.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_freeze_sha256:
        raise ValueError('Freeze checksum mismatch')
    freeze = json.loads(raw)
    if set(freeze['sources']) != {'Meta_Data.csv', 'Original_Features.csv'}:
        raise ValueError('Unexpected source set')
    for name, sha in {**freeze['sources'], 'model.joblib': freeze['model_sha256']}.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != sha:
            raise ValueError('Artifact checksum mismatch')
    with (root / 'Meta_Data.csv').open() as f: meta = list(csv.DictReader(f))
    with (root / 'Original_Features.csv').open() as f: rows = list(csv.DictReader(f))
    features = {r['number']: r for r in rows}
    if len(features) != len(rows) or len({r['number'] for r in meta}) != len(meta):
        raise ValueError('Duplicate identifiers')
    if set(features) != {r['number'] for r in meta}:
        raise ValueError('Identifier mismatch')
    if any(r['dataset'] not in {'train', 'test'} for r in meta):
        raise ValueError('Unknown partition')
    test = [r for r in meta if r['dataset'] == 'test']
    names = freeze['features']
    if not names or len(names) != len(set(names)):
        raise ValueError('Invalid feature order')
    x = np.array([[float(features[r['number']][n]) for n in names] for r in test])
    if not np.isfinite(x).all(): raise ValueError('Nonfinite features')
    # Deserialization follows external freeze hash and all payload integrity checks.
    model = joblib.load(root / 'model.joblib')
    scores = -model.score_samples(x)
    return dict(model_sha256=freeze['model_sha256'], freeze_sha256=expected_freeze_sha256,
                rows=len(test), decision_sha256=decision_digest([r['number'] for r in test], scores, freeze['cutoff']),
                alerts=int(np.sum(scores > freeze['cutoff'])), threshold=freeze['cutoff'])


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path); p.add_argument('freeze_sha256')
    a = p.parse_args(); print(json.dumps(verify(a.root, a.freeze_sha256), sort_keys=True))
