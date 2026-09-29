"""Reproducible, frozen-protocol Lenze feature benchmark."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score


def calibration_variant(variant):
    return int(hashlib.sha256(('lenze-v1:' + variant).encode()).hexdigest(), 16) % 5 == 0


def metrics(labels, scores, cutoff):
    y = np.asarray(labels, dtype=bool)
    alerts = np.asarray(scores) > cutoff
    tp = int(np.sum(y & alerts)); fp = int(np.sum(~y & alerts))
    recall = tp / int(y.sum()) if y.any() else 0.0
    fraction = fp / len(y)
    return dict(rows=len(y), anomalies=int(y.sum()), true_alerts=tp, false_alerts=fp,
                recall=recall, false_alert_fraction_of_all_rows=fraction,
                passed=recall >= .5 and fraction <= .1,
                roc_auc=float(roc_auc_score(y, scores)) if len(set(y)) == 2 else None)


def run(source, output):
    output.mkdir(parents=True, exist_ok=False)
    meta_path = source / 'Meta_Data.csv'; feature_path = source / 'Original_Features.csv'
    meta = list(csv.DictReader(meta_path.open(encoding='utf-8-sig')))
    rows = list(csv.DictReader(feature_path.open(encoding='utf-8-sig')))
    features = {r['number']: r for r in rows}
    if len(features) != len(rows) or len({r['number'] for r in meta}) != len(meta):
        raise ValueError('Duplicate identifiers')
    if set(features) != {r['number'] for r in meta}:
        raise ValueError('Identifier sets differ')
    if any(r['dataset'] not in {'train', 'test'} for r in meta):
        raise ValueError('Unexpected partition')
    names = [k for k in rows[0] if k != 'number' and not k.endswith('_opt')]
    def matrix(records):
        x = np.array([[float(features[r['number']][k]) for k in names] for r in records])
        if not np.isfinite(x).all():
            raise ValueError('Nonfinite features')
        return x
    train = [r for r in meta if r['dataset'] == 'train']
    if any(r['class_label'] != 'normal' for r in train):
        raise ValueError('Training must contain normal records only')
    fit = [r for r in train if not calibration_variant(r['A_Variant_ID'])]
    cal = [r for r in train if calibration_variant(r['A_Variant_ID'])]
    if not fit or not cal:
        raise ValueError('Empty fitting or calibration partition')
    model = IsolationForest(n_estimators=500, max_samples=256, random_state=42, n_jobs=1)
    model.fit(matrix(fit))
    cutoff = float(np.quantile(-model.score_samples(matrix(cal)), .95, method='higher'))
    model_path = output / 'model.joblib'
    joblib.dump(model, model_path)  # Local trusted artifact; never load untrusted pickle files.
    freeze = dict(cutoff=cutoff, features=names, fit_rows=len(fit), calibration_rows=len(cal),
                  model_sha256=hashlib.sha256(model_path.read_bytes()).hexdigest(),
                  sources={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (meta_path, feature_path)},
                  code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (output / 'freeze.json').write_text(json.dumps(freeze, indent=2))
    # All model choices and cutoff are persisted before scoring publisher test records.
    test = [r for r in meta if r['dataset'] == 'test']
    if any(r['class_label'] not in {'normal', 'anomalous'} for r in test):
        raise ValueError('Unknown target label')
    scores = -model.score_samples(matrix(test))
    report = metrics([r['class_label'] == 'anomalous' for r in test], scores, cutoff)
    report.update(scope='reference precomputed-feature benchmark', production_release='BLOCKED',
                  threshold=cutoff, features=len(names), fit_rows=len(fit), calibration_rows=len(cal))
    (output / 'evaluation.json').write_text(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path); p.add_argument('output', type=Path)
    args = p.parse_args()
    print(json.dumps(run(args.source, args.output), indent=2))
