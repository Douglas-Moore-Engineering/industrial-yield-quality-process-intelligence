import json
import csv
from pathlib import Path
import numpy as np
import pytest

from iyqpis.model_development import threshold_for_budget, forward_folds, guarded_metrics
from iyqpis.confirmation import confirm, read_confirmation_csv, wilson, row_fingerprint
from iyqpis.intelligence import fingerprint
from iyqpis.intelligence import FEATURES
from iyqpis.pipeline import write_json,digest


def test_threshold_budget_preserves_false_alert_denominator_and_includes_ties():
    y=np.array([1,1,0,0,0,0,0,0,0,0])
    p=np.array([.9,.6,.7,.5,.4,.3,.2,.1,.05,.01])
    threshold=threshold_for_budget(y,p)
    assert .5<threshold<.6
    assert ((p>=threshold)&(y==0)).sum()==1
    assert ((p>=threshold)&(y==1)).sum()==2
    # A tied false alert must count; do not split tied observations to force a pass.
    assert threshold_for_budget(np.array([1,0,0]),np.array([.5,.5,.2]),budget=0)>.5


def test_abstained_failures_are_not_removed_from_acceptance():
    m={'preprocessing':{'indices':[0],'median':[0.],'mean':[0.],'scale':[1.]},
       'coefficients':[1.],'intercept':0.,'calibration':{'slope':1.,'intercept':0.},'alert_threshold':.5,
       'guardrails':{'max_missing_fraction':.2,'max_abs_standardized_value':8.}}
    result=guarded_metrics(m,np.array([[99.],[99.],[99.],[1.],[-1.],[-1.]]),np.array([1,1,1,1,0,0]))
    assert result['recall']==.25 and not result['passed']
    assert result['abstentions']==3 and result['failures']==4


def test_forward_validation_is_strictly_later_than_training():
    times=[f'2026-01-{i:02d}' for i in range(1,21) for _ in range(2)]
    for train,valid in forward_folds(times):
        assert max(times[i] for i in train)<min(times[i] for i in valid)


def failed_bundle(root):
    m={'purpose':'unit-fixture'}
    m['model_id']=fingerprint(m)[:32]
    path=root/m['model_id']; path.mkdir()
    write_json(path/'model.json',m)
    write_json(path/'evaluation.json',{'model_id':m['model_id'],'calibration':{'passed':False}})
    write_json(path/'test-predictions.json',[])
    write_json(path/'manifest.json',{'status':'complete','model_id':m['model_id'],'artifacts':[
        {'path':n,'sha256':digest(path/n)} for n in ('model.json','evaluation.json','test-predictions.json')]})
    write_json(path/'freeze.json',{'model_id':m['model_id'],'manifest_sha256':digest(path/'manifest.json'),'calibration_gate_passed':False})
    return path


def test_failed_candidate_cannot_open_unseen_file(tmp_path):
    path=failed_bundle(tmp_path)
    with pytest.raises(ValueError,match='keep confirmation data sealed'):
        confirm(path,tmp_path/'absent-development',tmp_path/'absent-unseen.csv',tmp_path/'receipts',True)
    assert not (tmp_path/'receipts').exists()


def test_confirmation_requires_unseen_declaration_before_reading(tmp_path):
    with pytest.raises(ValueError,match='declaration'):
        confirm(tmp_path/'absent',tmp_path/'absent',tmp_path/'absent',tmp_path/'out')


def test_confirmation_schema_rejects_missing_sensors(tmp_path):
    path=tmp_path/'bad.csv'; path.write_text('event_time,failure\n2026-01-01T00:00:00Z,1\n')
    with pytest.raises(ValueError,match='sensor_590'):
        read_confirmation_csv(path)


def test_fingerprints_and_small_sample_uncertainty():
    assert row_fingerprint([1.,np.nan])==row_fingerprint([1.,float('nan')])
    assert wilson(1,1)[0]<.5
    assert wilson(0,0) is None


def passing_fixture(root):
    development=root/'development'; development.mkdir()
    write_json(development/'manifest.json',{'unit_fixture':True})
    m={'features':FEATURES,'preprocessing':{'indices':[0],'median':[0.],'mean':[0.],'scale':[1.]},
       'coefficients':[1.],'intercept':0.,'calibration':{'slope':1.,'intercept':0.},'alert_threshold':.5,
       'guardrails':{'max_missing_fraction':.2,'max_abs_standardized_value':8.},
       'acceptance_criteria':{'minimum_recall':.5,'maximum_false_alert_fraction_of_all_rows':.1},
       'data_manifest_sha256':digest(development/'manifest.json')}
    m['model_id']=fingerprint(m)[:32]
    path=root/m['model_id']; path.mkdir()
    write_json(path/'model.json',m)
    write_json(path/'evaluation.json',{'model_id':m['model_id'],'calibration':{'passed':True}})
    write_json(path/'test-predictions.json',[])
    write_json(path/'manifest.json',{'status':'complete','model_id':m['model_id'],'artifacts':[
        {'path':n,'sha256':digest(path/n)} for n in ('model.json','evaluation.json','test-predictions.json')]})
    write_json(path/'freeze.json',{'model_id':m['model_id'],'manifest_sha256':digest(path/'manifest.json'),'calibration_gate_passed':True})
    data=root/'new.csv'
    with data.open('w',newline='') as stream:
        writer=csv.writer(stream); writer.writerow(['event_time','failure']+FEATURES)
        writer.writerow(['2026-01-01T00:00:00Z',0,-1]+[0]*589)
        writer.writerow(['2026-01-02T00:00:00Z',1,1]+[0]*589)
    return path,development,data


def test_confirmation_is_one_shot_and_keeps_threshold_fixed(tmp_path,monkeypatch):
    bundle,development,data=passing_fixture(tmp_path)
    monkeypatch.setattr('iyqpis.confirmation.load_features',lambda _: (np.full((1,590),.25),None,['2008-01-01T00:00:00+00:00'],None,None))
    before=digest(bundle/'model.json')
    result=confirm(bundle,development,data,tmp_path/'out',True)
    assert result['acceptance_passed'] and result['threshold']==.5
    assert digest(bundle/'model.json')==before
    assert result['production_release']=='BLOCKED'
    with pytest.raises(FileExistsError):
        confirm(bundle,development,data,tmp_path/'different-output',True)


def test_confirmation_rejects_reused_features(tmp_path,monkeypatch):
    bundle,development,data=passing_fixture(tmp_path)
    old=np.zeros((1,590)); old[0,0]=-1
    monkeypatch.setattr('iyqpis.confirmation.load_features',lambda _: (old,None,['2008-01-01T00:00:00+00:00'],None,None))
    with pytest.raises(ValueError,match='overlap'):
        confirm(bundle,development,data,tmp_path/'out',True)
    assert json.loads((tmp_path/'out'/(bundle.name+'.json')).read_text())['status']=='rejected'
