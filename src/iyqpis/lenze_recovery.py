"""Non-destructive recovery drill against temporary copies of a frozen release."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time

from iyqpis.lenze_verification import verify


def drill(source: Path, freeze_sha: str, expected_decision_sha: str) -> dict:
    original = verify(source, freeze_sha)
    if original['decision_sha256'] != expected_decision_sha:
        raise ValueError('Approved decision identity mismatch')
    files = ['freeze.json', 'model.joblib', 'Meta_Data.csv', 'Original_Features.csv']
    before = {n: hashlib.sha256((source/n).read_bytes()).hexdigest() for n in files}
    cases = []
    with tempfile.TemporaryDirectory(prefix='lenze-recovery-') as directory:
        target = Path(directory)
        for name in files: shutil.copyfile(source/name, target/name)
        for name in files:
            for fault in ('missing', 'corrupt'):
                if fault == 'missing': (target/name).unlink()
                else:
                    with (target/name).open('ab') as f: f.write(b'corruption-drill')
                refused = False
                try: verify(target, freeze_sha)
                except (ValueError, FileNotFoundError): refused = True
                if not refused: raise AssertionError('Fault accepted: ' + name)
                start = time.perf_counter()
                shutil.copyfile(source/name, target/name)
                restored = verify(target, freeze_sha)
                if restored != original: raise AssertionError('Restored decisions differ')
                cases.append(dict(artifact=name, fault=fault, refused=True,
                                  restored_identically=True, restore_and_verify_seconds=time.perf_counter()-start))
    after = {n: hashlib.sha256((source/n).read_bytes()).hexdigest() for n in files}
    if before != after: raise AssertionError('Original release changed')
    return dict(scope='local temporary-copy artifact recovery drill', cases=cases,
                source_unchanged=True, decision_sha256=expected_decision_sha,
                model_sha256=original['model_sha256'], passed=True,
                production_rto_verified=False, azure_storage_restore_verified=False,
                rollback_scope='restore identical frozen artifacts; not active service promotion rollback')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('freeze_sha');p.add_argument('decision_sha');p.add_argument('output',type=Path)
    a=p.parse_args();report=drill(a.source,a.freeze_sha,a.decision_sha)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x') as f: json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(passed=report['passed'],cases=len(report['cases']),source_unchanged=True)))
