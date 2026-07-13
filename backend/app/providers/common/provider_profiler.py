import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class ProviderProfiler:
    """
    Performance tuning and diagnostics for API latency.
    Tracks precise execution time of provider calls.
    """
    @staticmethod
    def profile(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            
            logger.info(f"[PROFILER] {func.__name__} took {duration:.4f} seconds")
            return result
        return wrapper
