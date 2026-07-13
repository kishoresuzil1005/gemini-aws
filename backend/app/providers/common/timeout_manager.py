import signal
from contextlib import contextmanager
from app.providers.common.errors import TimeoutError

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutError("Timed out!")
    
    # This only works on UNIX/Linux
    try:
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        yield
    finally:
        try:
            signal.alarm(0)
        except Exception:
            pass
