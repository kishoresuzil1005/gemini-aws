"""Shared deterministic settings for analyzer certification tests."""

import pytest


@pytest.fixture
def num_nodes() -> int:
    """Representative graph size for the dependency performance test."""
    return 1_000


@pytest.fixture
def num_threads() -> int:
    """Bounded concurrency level for the dependency thread-safety test."""
    return 8
