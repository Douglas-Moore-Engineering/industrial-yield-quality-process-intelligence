import json
from pathlib import Path

import pytest

from iyqpis import pipeline
from iyqpis.contracts import validate_record
from test_contracts import VALID_TELEMETRY


@pytest.fixture
def sample(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    (raw / "fixture").mkdir(parents=True)
    (raw / "fixture/input.csv").write_text("immutable\n", encoding="utf-8")
    def install(records):
        def adapter(path, ingest_time):
            yield from records
        monkeypatch.setattr(pipeline, "ADAPTERS", {"fixture": {"telemetry": adapter}})
    install([dict(VALID_TELEMETRY)])
    return raw, tmp_path / "runs", install


def test_replay_and_corruption_detection(sample):
    raw, runs, _ = sample
    run = pipeline.build_run(raw, runs, "2026-01-01T00:00:05Z")
    assert pipeline.build_run(raw, runs, "2026-01-01T00:00:05Z") == run
    assert (raw / "fixture/input.csv").read_text() == "immutable\n"
    (run / "validated/fixture/telemetry.jsonl").write_text("corrupted")
    with pytest.raises(ValueError, match="checksum"):
        pipeline.build_run(raw, runs, "2026-01-01T00:00:05Z")


def test_bad_values_preserved_but_excluded_from_aggregates(sample):
    raw, runs, install = sample
    install([dict(VALID_TELEMETRY), dict(VALID_TELEMETRY, event_id="bad", quality_flag="BAD", value=0)])
    run = pipeline.build_run(raw, runs, "2026-01-01T00:00:05Z")
    summary = json.loads((run / "contextualized/fixture/stream-summary.jsonl").read_text())
    assert summary["records"] == 2
    assert summary["good_records"] == 1
    assert summary["mean"] == 1.23


@pytest.mark.parametrize("record", [dict(VALID_TELEMETRY, event_time="invalid"),
                                    dict(VALID_TELEMETRY, value=float("nan"))])
def test_invalid_run_never_published(sample, record):
    raw, runs, install = sample
    install([record])
    with pytest.raises(ValueError):
        pipeline.build_run(raw, runs, "2026-01-01T00:00:05Z")
    assert not list(runs.glob("*/manifest.json"))
    assert list(runs.glob(".pending-*/failure.json"))


def test_duplicate_events_reject_entire_batch(sample):
    raw, runs, install = sample
    install([dict(VALID_TELEMETRY), dict(VALID_TELEMETRY)])
    with pytest.raises(pipeline.sqlite3.IntegrityError):
        pipeline.build_run(raw, runs, "2026-01-01T00:00:05Z")
    assert not list(runs.glob("*/manifest.json"))


def test_output_cannot_overlap_raw(sample):
    raw, _, _ = sample
    with pytest.raises(ValueError, match="outside"):
        pipeline.build_run(raw, raw / "output", "2026-01-01T00:00:05Z")


def test_datetime_format_is_enforced():
    assert validate_record(dict(VALID_TELEMETRY, event_time="not-a-date"), "telemetry")


def test_source_change_prevents_promotion(sample, monkeypatch):
    raw, runs, _ = sample
    def changing_adapter(path, ingest_time):
        yield dict(VALID_TELEMETRY)
        (path / "input.csv").write_text("changed")
    monkeypatch.setattr(pipeline, "ADAPTERS", {"fixture": {"telemetry": changing_adapter}})
    with pytest.raises(ValueError, match="changed"):
        pipeline.build_run(raw, runs, "2026-01-01T00:00:05Z")
    assert not list(runs.glob("*/manifest.json"))
