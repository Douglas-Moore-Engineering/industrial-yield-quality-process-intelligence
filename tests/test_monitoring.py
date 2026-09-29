from iyqpis.monitoring import observe

B={'features':{'x':{'quantiles':{'p01':0,'p99':10}}}}

def test_unlabeled_batch_does_not_claim_performance():
    r=observe([[5]],B,[.1],.5)
    assert r['performance_passed'] is None and not r['drift_review_required']

def test_shift_is_review_signal_and_invalid_input_fails():
    assert observe([[20]],B,[.1],.5)['drift_review_required']
    assert not observe([[float('nan')]],B,[.1],.5)['data_quality_passed']

def test_performance_failure_detected_without_moving_threshold():
    r=observe([[5],[5]],B,[.1,.1],.5,[1,0])
    assert r['performance_passed'] is False

def test_invalid_label_and_score_shapes_refused():
    assert observe([[5]],B,[],.5)['status']=='failed'
    assert observe([[5]],B,[.1],.5,[2])['status']=='failed'
