"""Fixed, forward-validation experiment; never uses the legacy test for selection."""
import argparse
from pathlib import Path
import json
import warnings
import platform
from datetime import datetime, timezone

import numpy as np
import sklearn
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.feature_selection import f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.utils.class_weight import compute_sample_weight

from iyqpis.intelligence import (FEATURES, load_features, temporal_partitions, fit_preprocessor,
                                transform, metrics, fingerprint, probabilities, verify_bundle)
from iyqpis.pipeline import write_json, digest


def candidate_specs():
    specs = []
    for count in (10, 30, 100):
        for c in (.01, .1, 1.):
            specs.append({"family": "logistic", "features": count, "C": c})
    for family in ("random_forest", "extra_trees"):
        for count in (20, 60):
            for leaf in (3, 10):
                specs.append({"family": family, "features": count, "leaf": leaf})
    for count in (20, 60):
        specs.append({"family": "gradient_boosting", "features": count})
    return specs


def refinement_specs():
    return [{'family':'logistic','features':k,'C':c} for k in (3,5,8,12,15,20,40,60)
            for c in (.0001,.001,.003,.03,.3)]


def fit_candidate(x, y, spec):
    prep = fit_preprocessor(x)
    z = transform(x, prep)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        score, _ = f_classif(z, y)
    keep = np.argsort(-np.nan_to_num(score, nan=-np.inf), kind='stable')[:spec['features']]
    prep = {key: [values[i] for i in keep] for key, values in prep.items()}
    z = transform(x, prep)
    family = spec['family']
    if family == 'logistic':
        estimator = LogisticRegression(C=spec['C'], class_weight='balanced', max_iter=3000, random_state=0)
    elif family in {'random_forest', 'extra_trees'}:
        cls = RandomForestClassifier if family == 'random_forest' else ExtraTreesClassifier
        estimator = cls(n_estimators=200, min_samples_leaf=spec['leaf'], max_depth=8,
                        class_weight='balanced', random_state=0, n_jobs=1)
    else:
        estimator = GradientBoostingClassifier(n_estimators=150, learning_rate=.05, max_depth=2,
                                               min_samples_leaf=10, random_state=0)
    if family == 'gradient_boosting':
        estimator.fit(z, y, sample_weight=compute_sample_weight('balanced', y))
    else:
        estimator.fit(z, y)
    return prep, estimator


def threshold_for_budget(y, scores, budget=.1, eligible_rows=None):
    y, scores = np.asarray(y), np.asarray(scores)
    if len(y) == 0 or len(y) != len(scores) or set(y) != {0, 1} or not np.isfinite(scores).all():
        raise ValueError('Threshold fitting needs finite scores and both observed classes')
    options = np.unique(np.r_[scores, np.nextafter(scores.max(), np.inf)])
    eligible = []
    eligible_rows = np.ones(len(y),dtype=bool) if eligible_rows is None else np.asarray(eligible_rows,dtype=bool)
    if eligible_rows.shape != y.shape:
        raise ValueError('Eligibility shape mismatch')
    for threshold in options:
        alerts = (scores >= threshold) & eligible_rows
        false = int(((y == 0) & alerts).sum())
        true = int(((y == 1) & alerts).sum())
        if false / len(y) <= budget:
            eligible.append((true, -false, float(threshold)))
    cutoff=max(eligible)[2]
    lower=options[options<cutoff]
    # Put a real decision boundary between score groups, not exactly on a
    # calibration row's floating-point score. This preserves ties and decisions
    # while avoiding last-bit CPU/library differences flipping a boundary row.
    if len(lower) and cutoff<=scores.max():
        return float(lower[-1]+(cutoff-lower[-1])/2)
    return cutoff


def guard_mask(model, x):
    x=np.asarray(x,dtype=float)
    z=transform(x,model['preprocessing'])
    return (~np.isinf(x).any(axis=1) &
            (np.isnan(x).mean(axis=1) <= model['guardrails']['max_missing_fraction']) &
            (np.abs(z).max(axis=1) <= model['guardrails']['max_abs_standardized_value']))


def guarded_metrics(model, x, y):
    x,y=np.asarray(x,dtype=float),np.asarray(y)
    if x.ndim!=2 or len(x)==0 or y.shape!=(len(x),) or not set(y)<={0,1}:
        raise ValueError('Invalid labeled acceptance batch')
    p=probabilities(model,x)
    eligible=guard_mask(model,x)
    alerts=(p >= model['alert_threshold']) & eligible
    tp=int(((y==1)&alerts).sum())
    fp=int(((y==0)&alerts).sum())
    positives=int(y.sum())
    recall=tp/positives if positives else None
    fraction=fp/len(y)
    return {'rows':len(y),'failures':positives,'true_alerts':tp,'false_alerts':fp,
            'missed_failures':positives-tp,'abstentions':int((~eligible).sum()),
            'coverage':float(eligible.mean()),'recall':recall,
            'false_alert_fraction_of_all_rows':fraction,
            'passed':bool(recall is not None and recall>=.5 and fraction<=.1),
            'raw_classifier':metrics(y,p,model['alert_threshold'])}


def freeze_candidate(run, selection_path, output):
    run,output=run.resolve(),output.resolve()
    if output==run or output.is_relative_to(run):
        raise ValueError('Candidate output must be outside verified inputs')
    selection=json.loads(selection_path.read_text())
    if selection['data_manifest_sha256'] != digest(run/'manifest.json'):
        raise ValueError('Selection/data mismatch')
    x,y,times,keys,source=load_features(run)
    train,calibration,legacy=temporal_partitions(times)
    if selection.get('experiment')=='secom-quality-v3-expanded-development':
        train,calibration=np.r_[train,calibration],legacy
    spec=selection['selected']
    if spec['family'] != 'logistic':
        raise ValueError('Only the selected numeric logistic runtime is currently supported')
    prep,estimator=fit_candidate(x[train],y[train],spec)
    raw=estimator.decision_function(transform(x[calibration],prep)).reshape(-1,1)
    calibrator=LogisticRegression(C=1.,max_iter=3000,random_state=0).fit(raw,y[calibration])
    if calibrator.coef_[0][0] <= 0:
        raise ValueError('Calibration does not preserve ranking; candidate is not ready')
    model={'schema_version':1,'purpose':'sample_quality_candidate_v2','production_approved':False,
           'feature_version':'secom-sensors-v2-selected','features':FEATURES,'source_system':'sample:secom',
           'preprocessing':prep,'coefficients':estimator.coef_[0].tolist(),'intercept':float(estimator.intercept_[0]),
           'calibration':{'slope':float(calibrator.coef_[0][0]),'intercept':float(calibrator.intercept_[0])},
           'guardrails':{'max_missing_fraction':.2,'max_abs_standardized_value':8.,'max_age_seconds':300},
           'data_run_id':source['run_id'],'data_manifest_sha256':digest(run/'manifest.json'),
           'selection_report_sha256':digest(selection_path),'training_parameters':spec,
           'implementation':{n:digest(Path(__file__).with_name(n)) for n in ('model_development.py','intelligence.py')},
           'runtime':{'python':platform.python_version(),'numpy':np.__version__,'sklearn':sklearn.__version__},
           'acceptance_criteria':{'minimum_recall':.5,'maximum_false_alert_fraction_of_all_rows':.1}}
    p=probabilities(model,x[calibration])
    model['alert_threshold']=threshold_for_budget(y[calibration],p,eligible_rows=guard_mask(model,x[calibration]))
    model['model_id']=fingerprint(model)[:32]
    path=output/model['model_id']
    if path.exists():
        verify_bundle(path)
        return path
    report={'model_id':model['model_id'],'scope':'development/calibration only; NOT final acceptance',
            'selected':spec,'calibration':guarded_metrics(model,x[calibration],y[calibration]),
            'legacy_test_reclassified_for_development':selection.get('experiment')=='secom-quality-v3-expanded-development',
            'confirmation_used':False,'production_release':'BLOCKED'}
    path.mkdir(parents=True)
    write_json(path/'model.json',model)
    write_json(path/'evaluation.json',report)
    # Kept for compatibility with the existing bundle verifier; no held-out rows are included.
    write_json(path/'test-predictions.json',[])
    write_json(path/'manifest.json',{'status':'complete','model_id':model['model_id'],
               'artifacts':[{'path':n,'sha256':digest(path/n)} for n in ('model.json','evaluation.json','test-predictions.json')]})
    write_json(path/'freeze.json',{'model_id':model['model_id'],'manifest_sha256':digest(path/'manifest.json'),
               'frozen_at':datetime.now(timezone.utc).isoformat(),'confirmation_used':False,
               'calibration_gate_passed':report['calibration']['passed']})
    print(json.dumps({'model_id':model['model_id'],'calibration':report['calibration']}),flush=True)
    return path


def forward_folds(times):
    unique = sorted(set(times))
    result = []
    for fraction in (.4, .55, .7):
        start, end = unique[int(len(unique)*fraction)], unique[int(len(unique)*(fraction+.15))]
        train = np.array([i for i,t in enumerate(times) if t < start])
        validation = np.array([i for i,t in enumerate(times) if start <= t < end])
        result.append((train, validation))
    return result


def experiment(run, output):
    x, y, times, keys, manifest = load_features(run)
    original_train, calibration, legacy = temporal_partitions(times)
    # Explicitly discard all later rows before candidate selection.
    x, y = x[original_train], y[original_train]
    times = [times[i] for i in original_train]
    folds = forward_folds(times)
    results = []
    for spec in candidate_specs():
        scores = []
        for train, valid in folds:
            if len(set(y[train])) != 2 or len(set(y[valid])) != 2:
                raise ValueError('Forward fold lacks both classes')
            prep, estimator = fit_candidate(x[train], y[train], spec)
            p = estimator.predict_proba(transform(x[valid], prep))[:,1]
            threshold = threshold_for_budget(y[valid], p)
            scores.append(metrics(y[valid], p, threshold))
        entry = {'spec': spec, 'folds': scores, 'mean_average_precision': float(np.mean([s['average_precision'] for s in scores]))}
        results.append(entry)
        print(json.dumps({'candidate': spec, 'mean_average_precision': entry['mean_average_precision']}), flush=True)
    selected = max(results, key=lambda item:item['mean_average_precision'])
    report = {'experiment':'secom-quality-v2', 'data_run_id':manifest['run_id'],
              'data_manifest_sha256':digest(run/'manifest.json'),
              'selection_scope':'original training partition, forward validation only',
              'legacy_test_used_for_selection':False, 'confirmation_used':False,
              'selected':selected['spec'], 'candidates':results,
              'acceptance_criteria':{'minimum_recall':.5,'maximum_false_alert_fraction_of_all_rows':.1}}
    write_json(output, report)
    print(json.dumps({'selected':report['selected']}))
    return report


def refinement(run,output):
    x,y,times,keys,source=load_features(run)
    a,b,dev=temporal_partitions(times)
    train=np.r_[a,b]
    results=[]
    for spec in refinement_specs():
        prep,estimator=fit_candidate(x[train],y[train],spec)
        p=estimator.predict_proba(transform(x[dev],prep))[:,1]
        mask=guard_mask({'preprocessing':prep,'guardrails':{'max_missing_fraction':.2,'max_abs_standardized_value':8.}},x[dev])
        threshold=threshold_for_budget(y[dev],p,eligible_rows=mask)
        alerts=(p>=threshold)&mask
        row={'spec':spec,'recall':float(y[dev][alerts].sum()/y[dev].sum()),
             'false_alerts':int(((y[dev]==0)&alerts).sum()),'abstentions':int((~mask).sum()),
             'average_precision':float(average_precision_score(y[dev],p))}
        results.append(row)
        print(json.dumps(row),flush=True)
    selected=max(results,key=lambda r:(r['recall'],-r['false_alerts'],r['average_precision']))
    report={'experiment':'secom-quality-v3-expanded-development','scope':'development only; NO fresh acceptance',
            'data_manifest_sha256':digest(run/'manifest.json'),'selected':selected['spec'],'results':results,
            'confirmation_used':False}
    write_json(output,report)
    print(json.dumps({'selected':selected}),flush=True)
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data_run',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--freeze-selection',type=Path)
    parser.add_argument('--refine-exposed-development',action='store_true')
    args=parser.parse_args()
    if args.freeze_selection:
        freeze_candidate(args.data_run,args.freeze_selection,args.output)
    elif args.refine_exposed_development:
        refinement(args.data_run,args.output)
    else:
        experiment(args.data_run,args.output)
