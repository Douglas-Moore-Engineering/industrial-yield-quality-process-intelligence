import pytest
from iyqpis.lenze_verification import decision_digest, verify


def test_same_counts_different_records_are_detected():
    assert decision_digest(['a','b'], [.9,.1], .5) != decision_digest(['a','b'], [.1,.9], .5)


def test_row_order_does_not_change_identity():
    assert decision_digest(['a','b'], [.9,.1], .5) == decision_digest(['b','a'], [.1,.9], .5)


@pytest.mark.parametrize('ids,scores', [(['a','a'],[.1,.2]), (['a'],[float('nan')]), (['a'],[float('inf')]), (['a'],[])])
def test_invalid_predictions_refused(ids,scores):
    with pytest.raises(ValueError): decision_digest(ids,scores,.5)


def test_freeze_tampering_rejected_before_loading_model(tmp_path):
    (tmp_path/'freeze.json').write_text('{}')
    with pytest.raises(ValueError,match='Freeze checksum'):
        verify(tmp_path, '0'*64)
