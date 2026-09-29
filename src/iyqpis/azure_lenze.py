"""Verify the exact frozen Lenze model; optionally publish private Azure evidence."""
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile

import joblib
import numpy as np

from iyqpis.lenze import metrics
from iyqpis.monitoring import observe


def main():
    root = Path('/app/lenze')
    freeze = json.loads((root / 'freeze.json').read_text())
    for name, expected in {**freeze['sources'], 'model.joblib': freeze['model_sha256']}.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen artifact mismatch')
    # Only the checksum-verified, locally built model is deserialized.
    model = joblib.load(root / 'model.joblib')
    with (root / 'Meta_Data.csv').open() as f:
        test = [r for r in csv.DictReader(f) if r['dataset'] == 'test']
    with (root / 'Original_Features.csv').open() as f:
        features = {r['number']: r for r in csv.DictReader(f)}
    x = np.array([[float(features[r['number']][k]) for k in freeze['features']] for r in test])
    if not np.isfinite(x).all():
        raise ValueError('Nonfinite inputs')
    scores = -model.score_samples(x)
    labels = [r['class_label'] == 'anomalous' for r in test]
    baseline = json.loads((root / 'baseline.json').read_text())
    if list(baseline['features']) != freeze['features'] or baseline['frozen_model_sha256'] != freeze['model_sha256']:
        raise ValueError('Monitoring baseline mismatch')
    print(json.dumps(observe(x, baseline, scores, freeze['cutoff'], labels)), flush=True)
    report = metrics(labels, scores, freeze['cutoff'])
    expected = json.loads((root / 'evaluation.json').read_text())
    for key in ('rows', 'anomalies', 'true_alerts', 'false_alerts', 'passed'):
        if report[key] != expected[key]:
            raise ValueError('Cloud/local decision mismatch: ' + key)
    report.update(model_sha256=freeze['model_sha256'], production_release='BLOCKED',
                  scope='frozen reference model verification', exact_decisions_match=True)
    if os.environ.get('LENZE_PUBLISH') == '1':
        from azure.identity import ManagedIdentityCredential
        from azure.storage.blob import BlobServiceClient
        from iyqpis.azure_batch import require_private_dns, put_verified
        host = os.environ['DATA_STORAGE_ACCOUNT'] + '.blob.core.windows.net'
        require_private_dns(host)
        with ManagedIdentityCredential(client_id=os.environ['AZURE_CLIENT_ID']) as identity:
            with BlobServiceClient('https://' + host, credential=identity) as service:
                prefix = 'lenze/' + freeze['model_sha256']
                with tempfile.TemporaryDirectory() as tmp:
                    evidence = Path(tmp) / 'azure-verification.json'
                    evidence.write_text(json.dumps(report, indent=2))
                    for p in (root / 'model.joblib', root / 'freeze.json', root / 'evaluation.json', evidence):
                        put_verified(service.get_blob_client('curated-evidence', prefix + '/' + p.name),
                                     p, hashlib.sha256(p.read_bytes()).hexdigest())
    print(json.dumps(report))


if __name__ == '__main__':
    main()
