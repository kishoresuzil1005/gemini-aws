import time
import logging
from typing import Callable, Any
from app.providers.common.errors import TimeoutError, ProviderError

logger = logging.getLogger(__name__)

class BaseService:
    """Common patterns for all provider services (retry, metrics, exception conversion)."""
    
    def _execute_with_retry(self, func: Callable, max_retries: int = 3, backoff: float = 2.0, *args, **kwargs) -> Any:
        """Executes a function with exponential backoff retries."""
        attempt = 0
        while attempt < max_retries:
            try:
                # We could hook provider_metrics.record_api_call here
                start = time.time()
                res = func(*args, **kwargs)
                duration = time.time() - start
                
                # Success
                return res
            except Exception as e:
                attempt += 1
                logger.warning(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
                if attempt >= max_retries:
                    # Exception conversion is typically done by the caller using their specific mapping logic,
                    # but we re-raise the final error here.
                    raise
                time.sleep(backoff ** attempt)
