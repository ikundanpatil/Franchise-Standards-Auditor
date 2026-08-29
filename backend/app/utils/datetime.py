"""Timezone-aware ``now`` helpers so timestamps are consistent everywhere."""

from __future__ import annotations

from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


def isoformat(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None
