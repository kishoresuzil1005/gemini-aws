import time

class RateLimiter:
    """Simple token bucket or sleep-based rate limiting to avoid provider throttling."""
    def __init__(self, calls_per_second: float):
        self.interval = 1.0 / calls_per_second
        self.last_call = 0.0

    def wait(self):
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        self.last_call = time.time()
