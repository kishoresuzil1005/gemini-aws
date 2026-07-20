"""Simple validators shared across providers."""

from typing import Any


def is_non_empty_string(value: Any) -> bool:
    """Return True if *value* is a non-empty, non-whitespace string."""
    return isinstance(value, str) and bool(value.strip())


def is_valid_arn(value: Any) -> bool:
    """Return True if *value* looks like an AWS ARN."""
    return isinstance(value, str) and value.startswith("arn:")


def coerce_bool(value: Any, default: bool = False) -> bool:
    """Safely coerce a value to bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default
