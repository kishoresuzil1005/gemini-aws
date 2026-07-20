"""Shared helper utilities used across providers and analyzers."""

from datetime import datetime, timezone


def iso_timestamp() -> str:
    """Return the current UTC time as an ISO‑8601 string."""
    return datetime.now(timezone.utc).isoformat()


def flag_enabled(env_var: str, *, default: bool = True) -> bool:
    """Read a boolean feature flag from an environment variable.

    Parameters
    ----------
    env_var:
        The name of the environment variable to read.
    default:
        The value to use when the variable is not set. Defaults to ``True``
        so that providers are opt-out rather than opt-in.
    """
    import os
    raw = os.getenv(env_var)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def elapsed_ms(start: datetime) -> float:
    """Return milliseconds elapsed since *start* (UTC)."""
    return (datetime.now(timezone.utc) - start.replace(tzinfo=timezone.utc)).total_seconds() * 1000
