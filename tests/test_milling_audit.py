import pytest

from iyqpis.milling_audit import audit


def source(rows):
    return ('6;;;;;;\nAcelR fz Diam ae HB geom;;;;;;\n1;;;;;;\nRa;;;;;;\n'
            + str(len(rows)) + ';;;;;;\n' + '\n'.join(rows)).encode()


def test_group_assignment_does_not_depend_on_target_or_vibration():
    data = source(['1.606.100;0.1;16.000.000;2.000.000;145.000.000;0.021;0.34',
                   '9.000.000;0.1;16.000.000;2.000.000;145.000.000;0.021;999'])
    report = audit(data)
    assert report['row_groups'][0] == report['row_groups'][1]
    assert report['setting_groups'] == 1
    assert report['ambiguous_input_cells'] == 8
    assert not report['training_ready']
    assert not report['outcomes_evaluated']


def test_malformed_width_rejected():
    with pytest.raises(ValueError, match='width'):
        audit(source(['1;2;3']))
