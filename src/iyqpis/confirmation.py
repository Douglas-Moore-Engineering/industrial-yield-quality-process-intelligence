"""One-shot reference acceptance of a frozen candidate on separately supplied data.

This command does not train, recalibrate, select features, or change a threshold.
The caller must identify data not previously used for model development.
"""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path

import numpy as np

from iyqpis.intelligence import FEATURES, fingerprint, load_features, verify_bundle
from iyqpis.model_development import guarded_metrics
from iyqpis.pipeline import digest, write_json


def read_confirmation_csv(path):
    rows, outcomes, times = [], [], []
    with path.open(newline='',encoding='utf-8-sig') as stream:
        reader=csv.DictReader(stream)
        if reader.fieldnames is None or len(reader.fieldnames)!=len(set(reader.fieldnames)) or set(reader.fieldnames)!=set(FEATURES+['event_time','failure']):
            raise ValueError('Expected exactly event_time, failure and sensor_1 through sensor_590')
        for row in reader:
            if any(row.get(name) is None for name in FEATURES+['event_time','failure']) or None in row:
                raise ValueError('Malformed confirmation row')
            if row['failure'] not in {'0','1'}:
                raise ValueError('Failure label must be 0 or 1')
            at=datetime.fromisoformat(row['event_time'].replace('Z','+00:00'))
            if at.tzinfo is None:
                raise ValueError('Explicit timestamp timezone required')
            vector=[np.nan if row[name].strip() in {'','NaN','nan'} else float(row[name]) for name in FEATURES]
            if np.isinf(vector).any():
                raise ValueError('Infinite sensor value')
            rows.append(vector)
            outcomes.append(int(row['failure']))
            times.append(at.astimezone(timezone.utc).isoformat())
    if not rows or set(outcomes)!={0,1}:
        raise ValueError('Confirmation requires nonempty data with both outcome classes')
    return np.asarray(rows),np.asarray(outcomes),times


def row_fingerprint(row):
    return fingerprint([None if np.isnan(v) else float(v) for v in row])


def wilson(successes, count):
    if count == 0:
        return None
    z=1.959963984540054
    p=successes/count
    center=(p+z*z/(2*count))/(1+z*z/count)
    radius=z*((p*(1-p)/count+z*z/(4*count*count))**.5)/(1+z*z/count)
    return [max(0.,center-radius),min(1.,center+radius)]


def confirm(bundle, development_run, csv_path, output_root, declared_unseen=False):
    if not declared_unseen:
        raise ValueError('Explicit previously-unseen declaration required')
    model=verify_bundle(bundle)
    freeze=json.loads((bundle/'freeze.json').read_text())
    if freeze['model_id']!=model['model_id'] or freeze['manifest_sha256']!=digest(bundle/'manifest.json'):
        raise ValueError('Frozen bundle mismatch')
    report=json.loads((bundle/'evaluation.json').read_text())
    if not freeze['calibration_gate_passed'] or not report['calibration']['passed']:
        raise ValueError('Candidate failed calibration; keep confirmation data sealed')
    expected={'minimum_recall':.5,'maximum_false_alert_fraction_of_all_rows':.1}
    if model['acceptance_criteria']!=expected:
        raise ValueError('Acceptance criteria were changed')
    if digest(development_run/'manifest.json')!=model['data_manifest_sha256']:
        raise ValueError('Incorrect development data for overlap audit')
    # Reserve the candidate's single evaluation before reading confirmation rows.
    output_root.mkdir(parents=True,exist_ok=True)
    receipt=output_root/(model['model_id']+'.json')
    with (bundle/'confirmation-reservation.json').open('x',encoding='utf-8') as stream:
        json.dump({'model_id':model['model_id'],'reserved_at':datetime.now(timezone.utc).isoformat()},stream)
    with receipt.open('x',encoding='utf-8') as stream:
        json.dump({'status':'reserved','model_id':model['model_id'],'frozen_manifest_sha256':freeze['manifest_sha256']},stream)
    try:
        before=digest(csv_path)
        x,y,times=read_confirmation_csv(csv_path)
        old_x,_,old_times,_,_=load_features(development_run)
        old={row_fingerprint(row) for row in old_x}
        supplied=[row_fingerprint(row) for row in x]
        if len(set(supplied))!=len(supplied) or old.intersection(supplied):
            raise ValueError('Repeated confirmation rows or overlap with exposed data')
        if min(times)<=max(old_times):
            raise ValueError('Confirmation is not later than the exposed source period')
        if digest(csv_path)!=before:
            raise ValueError('Confirmation input changed during evaluation')
        result={'status':'evaluated','scope':'reference confirmation, not production release',
                'evaluator_sha256':digest(Path(__file__)),
                'model_id':model['model_id'],'frozen_manifest_sha256':freeze['manifest_sha256'],
                'input_sha256':before,'declared_previously_unseen':True,
                'no_exact_feature_row_overlap':True,'later_than_exposed_period':True,
                'threshold':model['alert_threshold'],'acceptance_criteria':expected,
                'guarded_metrics':guarded_metrics(model,x,y),'production_release':'BLOCKED',
                'evaluated_at':datetime.now(timezone.utc).isoformat()}
        gm=result['guarded_metrics']
        result['recall_95pct_wilson']=wilson(gm['true_alerts'],gm['failures'])
        result['false_alert_fraction_95pct_wilson']=wilson(gm['false_alerts'],gm['rows'])
        result['acceptance_passed']=gm['passed']
        write_json(receipt,result)
        return result
    except Exception as error:
        write_json(receipt,{'status':'rejected','model_id':model['model_id'],'error_type':type(error).__name__,
                            'note':'Evaluation reservation retained; do not relabel consumed data as unseen'})
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle',type=Path)
    parser.add_argument('development_run',type=Path)
    parser.add_argument('confirmation_csv',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--declare-previously-unseen',action='store_true')
    args=parser.parse_args()
    print(json.dumps(confirm(args.bundle,args.development_run,args.confirmation_csv,args.output,args.declare_previously_unseen)))
