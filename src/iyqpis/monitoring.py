"""Structured reference batch health events; no implied live-process evidence."""
import numpy as np
from iyqpis.lenze import metrics


def observe(x, baseline, scores, cutoff, labels=None):
    x = np.asarray(x, dtype=float)
    names = list(baseline['features'])
    valid = x.ndim == 2 and x.shape[1] == len(names) and len(x) > 0 and np.isfinite(x).all()
    report = dict(event_type='iyqpis_monitoring', schema_version=1,
                  scope='reference_batch', data_quality_passed=bool(valid),
                  performance_passed=None, drift_review_required=None,
                  status='failed' if not valid else 'observed')
    if not valid: return report
    scores = np.asarray(scores, dtype=float)
    if scores.shape != (len(x),) or not np.isfinite(scores).all() or not np.isfinite(cutoff):
        report.update(status='failed', data_quality_passed=False)
        return report
    low = np.array([baseline['features'][n]['quantiles']['p01'] for n in names])
    high = np.array([baseline['features'][n]['quantiles']['p99'] for n in names])
    outside = np.mean((x < low) | (x > high), axis=0)
    report.update(rows=len(x), alert_fraction=float(np.mean(scores > cutoff)),
                  outside_reference_fraction=dict(zip(names,map(float,outside))),
                  drift_review_required=bool(np.any(outside > .10)),
                  drift_policy='provisional: review if >10% outside training p01-p99 for any feature; not a production gate')
    if labels is not None:
        labels = np.asarray(labels)
        if labels.shape != (len(x),) or not np.isin(labels,[0,1]).all():
            report.update(status='failed',data_quality_passed=False)
            return report
        if np.any(labels == 1):
            result = metrics(labels, scores, cutoff)
            report.update(performance_passed=result['passed'], recall=result['recall'],
                          false_alert_fraction_of_all_rows=result['false_alert_fraction_of_all_rows'])
    return report
