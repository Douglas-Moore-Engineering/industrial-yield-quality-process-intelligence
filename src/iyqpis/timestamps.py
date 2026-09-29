"""Timestamp integrity checks required before genealogy reconstruction (docs/04-data-architecture-and-digital-thread.md)."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Iterable, Sequence


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def find_timestamp_anomalies(
    records: Iterable[dict],
    time_field: str = "event_time",
    group_fields: Sequence[str] = ("asset_id", "tag_id"),
) -> list[str]:
    """Flag missing/unparseable timestamps and out-of-order or duplicate timestamps within each group.

    Records are grouped by `group_fields` (e.g. per asset+tag telemetry stream); within a group,
    `time_field` is expected to be non-decreasing and non-duplicated, since deterministic replay
    depends on it. Pass `group_fields=()` to check a single global stream.
    """
    errors: list[str] = []
    last_seen: dict[tuple, datetime] = {}
    seen_times: dict[tuple, set[datetime]] = defaultdict(set)
    for i, record in enumerate(records):
        raw = record.get(time_field)
        if not raw:
            errors.append(f"record[{i}]: missing '{time_field}'")
            continue
        try:
            parsed = _parse(raw)
        except (ValueError, TypeError):
            errors.append(f"record[{i}]: unparseable '{time_field}'={raw!r}")
            continue
        key = tuple(record.get(f) for f in group_fields)
        if parsed in seen_times[key]:
            errors.append(f"record[{i}]: duplicate {time_field}={raw!r} for group {dict(zip(group_fields, key))}")
        seen_times[key].add(parsed)
        prior = last_seen.get(key)
        if prior is not None and parsed < prior:
            errors.append(
                f"record[{i}]: out-of-order {time_field}={raw!r} (< prior {prior.isoformat()}) "
                f"for group {dict(zip(group_fields, key))}"
            )
        last_seen[key] = parsed
    return errors
