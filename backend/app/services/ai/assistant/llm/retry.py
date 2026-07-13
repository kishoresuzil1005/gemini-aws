import time
import functools
from app.services.ai.assistant.llm.exceptions import LlmException, LlmConnectionError, LlmTimeoutError

def with_retry(max_retries=3, base_delay=1.0, backoff_factor=2.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except LlmException as e:
                    if not e.retryable:
                        raise
                    last_exception = e
                except Exception as e:
                    last_exception = e

                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= backoff_factor
            
            raise last_exception
        return wrapper
    return decorator