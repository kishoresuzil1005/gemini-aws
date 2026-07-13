import time
import logging
from typing import Callable, Any
from enum import Enum

logger = logging.getLogger(__name__)

class RetryProfile(Enum):
    FAST = (3, 1.0)
    CRITICAL = (5, 2.0)
    DISCOVERY = (10, 5.0)
    BACKGROUND = (3, 10.0)

class RetryEngine:
    """Provides exponential backoff retries with specific profiles."""
    @staticmethod
    def execute_with_retry(func: Callable, profile: RetryProfile = RetryProfile.FAST, *args, **kwargs) -> Any:
        max_retries, backoff = profile.value
        attempt = 0
        while attempt < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                logger.warning(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
                if attempt >= max_retries:
                    raise
                time.sleep(backoff ** attempt)
