"""
Telemetry (Phase 17)
=====================
Structured logging + optional Prometheus metric exports.
Falls back to Python logging when Prometheus is not installed.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger("cloudops.orchestrator")

# ---------------------------------------------------------------------------
# Optional Prometheus integration
# ---------------------------------------------------------------------------
try:
    from prometheus_client import Counter, Histogram, start_http_server  # type: ignore

    _ORCHESTRATOR_LATENCY = Histogram(
        "orchestrator_latency_seconds",
        "End-to-end orchestrator request latency",
        ["intent"],
    )
    _PROVIDER_LATENCY = Histogram(
        "provider_execution_seconds",
        "Per-provider execution latency",
        ["provider", "outcome"],
    )
    _CACHE_HIT = Counter("cache_hit_total", "Cache hits")
    _CACHE_MISS = Counter("cache_miss_total", "Cache misses")
    _RESOLUTION_SUCCESS = Counter("resolution_success_total", "Successful resource resolutions")
    _RESOLUTION_FAILURE = Counter("resolution_failure_total", "Failed resource resolutions")
    _LLM_TOKENS = Counter("llm_token_usage_total", "LLM tokens consumed", ["direction"])
    _PROMETHEUS_AVAILABLE = True

except ImportError:
    _PROMETHEUS_AVAILABLE = False


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

@contextmanager
def track_orchestrator_latency(intent: str = "general"):
    """Context manager that records end-to-end latency."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(
            "[Telemetry] orchestrator latency=%.3fs intent=%s", elapsed, intent
        )
        if _PROMETHEUS_AVAILABLE:
            _ORCHESTRATOR_LATENCY.labels(intent=intent).observe(elapsed)


@contextmanager
def track_provider_latency(provider: str, outcome: str = "success"):
    """Context manager that records per-provider latency."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(
            "[Telemetry] provider=%s latency=%.3fs outcome=%s", provider, elapsed, outcome
        )
        if _PROMETHEUS_AVAILABLE:
            _PROVIDER_LATENCY.labels(provider=provider, outcome=outcome).observe(elapsed)


def record_cache_hit() -> None:
    if _PROMETHEUS_AVAILABLE:
        _CACHE_HIT.inc()


def record_cache_miss() -> None:
    if _PROMETHEUS_AVAILABLE:
        _CACHE_MISS.inc()


def record_resolution(success: bool) -> None:
    if _PROMETHEUS_AVAILABLE:
        if success:
            _RESOLUTION_SUCCESS.inc()
        else:
            _RESOLUTION_FAILURE.inc()


def record_llm_tokens(prompt_tokens: int, completion_tokens: int) -> None:
    logger.info(
        "[Telemetry] LLM tokens — prompt=%d completion=%d total=%d",
        prompt_tokens,
        completion_tokens,
        prompt_tokens + completion_tokens,
    )
    if _PROMETHEUS_AVAILABLE:
        _LLM_TOKENS.labels(direction="prompt").inc(prompt_tokens)
        _LLM_TOKENS.labels(direction="completion").inc(completion_tokens)
