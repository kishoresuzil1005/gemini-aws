"""Time utilities for the Context Engine."""

from datetime import datetime, timedelta, timezone


def utcnow() -> datetime:
    """Return an aware UTC datetime."""
    return datetime.now(timezone.utc)


def look_back_start(hours: int = 24) -> datetime:
    """Return an aware UTC datetime *hours* ago."""
    return utcnow() - timedelta(hours=hours)


def look_back_range(hours: int = 24):
    """Return (start, end) tuple of aware UTC datetimes for the look‑back window."""
    end = utcnow()
    start = end - timedelta(hours=hours)
    return start, end
