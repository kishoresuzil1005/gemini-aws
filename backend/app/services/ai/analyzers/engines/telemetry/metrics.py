"""
Telemetry Metrics.
Decorators for engines to automatically record execution metrics.
"""
import time
import functools
import logging

logger = logging.getLogger(__name__)

def record_metrics(engine_name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[TELEMETRY] {engine_name}.{func.__name__} executed in {duration_ms:.2f}ms")
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(f"[TELEMETRY] {engine_name}.{func.__name__} failed in {duration_ms:.2f}ms: {e}")
                raise
        return wrapper
    return decorator
