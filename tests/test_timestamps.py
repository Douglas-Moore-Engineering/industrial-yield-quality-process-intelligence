from iyqpis.timestamps import find_timestamp_anomalies


def test_clean_ordered_stream_has_no_anomalies():
    records = [
        {"asset_id": "a1", "tag_id": "t1", "event_time": "2026-01-01T00:00:00+00:00"},
        {"asset_id": "a1", "tag_id": "t1", "event_time": "2026-01-01T00:00:01+00:00"},
    ]
    assert find_timestamp_anomalies(records) == []


def test_missing_timestamp_flagged():
    records = [{"asset_id": "a1", "tag_id": "t1", "event_time": ""}]
    errors = find_timestamp_anomalies(records)
    assert len(errors) == 1 and "missing" in errors[0]


def test_unparseable_timestamp_flagged():
    records = [{"asset_id": "a1", "tag_id": "t1", "event_time": "not-a-date"}]
    errors = find_timestamp_anomalies(records)
    assert len(errors) == 1 and "unparseable" in errors[0]


def test_duplicate_timestamp_in_same_group_flagged():
    records = [
        {"asset_id": "a1", "tag_id": "t1", "event_time": "2026-01-01T00:00:00+00:00"},
        {"asset_id": "a1", "tag_id": "t1", "event_time": "2026-01-01T00:00:00+00:00"},
    ]
    errors = find_timestamp_anomalies(records)
    assert len(errors) == 1 and "duplicate" in errors[0]


def test_out_of_order_timestamp_in_same_group_flagged():
    records = [
        {"asset_id": "a1", "tag_id": "t1", "event_time": "2026-01-01T00:00:05+00:00"},
        {"asset_id": "a1", "tag_id": "t1", "event_time": "2026-01-01T00:00:00+00:00"},
    ]
    errors = find_timestamp_anomalies(records)
    assert len(errors) == 1 and "out-of-order" in errors[0]


def test_different_groups_do_not_interfere():
    records = [
        {"asset_id": "a1", "tag_id": "t1", "event_time": "2026-01-01T00:00:05+00:00"},
        {"asset_id": "a2", "tag_id": "t1", "event_time": "2026-01-01T00:00:00+00:00"},
    ]
    assert find_timestamp_anomalies(records) == []
