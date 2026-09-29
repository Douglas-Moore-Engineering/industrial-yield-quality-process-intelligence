import hashlib
import json
import pytest
from iyqpis.lenze_baseline import build


def fixture(tmp_path):
    (tmp_path/'Meta_Data.csv').write_text('number,dataset,class_label,A_Variant_ID\n1,train,normal,a\n2,test,anomalous,b\n')
    (tmp_path/'Original_Features.csv').write_text('number,x\n1,2\n2,99999\n')
    manifest={'sources':{n:hashlib.sha256((tmp_path/n).read_bytes()).hexdigest()
                         for n in ('Meta_Data.csv','Original_Features.csv')},
              'features':['x'],'model_sha256':'fixture'}
    freeze=tmp_path/'freeze.json';freeze.write_text(json.dumps(manifest))
    return freeze


def test_test_outliers_excluded_from_baseline(tmp_path):
    report=build(tmp_path,fixture(tmp_path))
    assert report['features']['x']['maximum']==2
    assert report['training_rows']==1
    assert not report['test_used']


def test_modified_source_refused(tmp_path):
    freeze=fixture(tmp_path)
    with (tmp_path/'Original_Features.csv').open('a') as f: f.write('3,5\n')
    with pytest.raises(ValueError,match='checksum'):
        build(tmp_path,freeze)
