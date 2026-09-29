from iyqpis.lenze import calibration_variant, metrics


def test_cutoff_is_strict_and_false_alert_denominator_is_all_rows():
    report = metrics([True, True, False, False], [.9, .5, .7, .1], .5)
    assert report['recall'] == .5
    assert report['false_alert_fraction_of_all_rows'] == .25
    assert not report['passed']


def test_variant_assignment_is_stable_and_has_both_partitions():
    values = [calibration_variant(str(i)) for i in range(100)]
    assert any(values) and not all(values)
    assert values == [calibration_variant(str(i)) for i in range(100)]
