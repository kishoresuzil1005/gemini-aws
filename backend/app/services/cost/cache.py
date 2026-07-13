import time
from threading import Lock

class CostSummaryCache:
    _data = None
    _last_refresh = 0
    _ttl_seconds = 300  # 5 minutes
    _lock = Lock()

    @classmethod
    def get(cls):
        if (
            cls._data is None or
            time.time() - cls._last_refresh > cls._ttl_seconds
        ):
            return None
        return cls._data

    @classmethod
    def set(cls, data):
        with cls._lock:
            cls._data = data
            cls._last_refresh = time.time()

    @classmethod
    def clear(cls):
        with cls._lock:
            cls._data = None
            cls._last_refresh = 0

    @classmethod
    def age(cls):
        if cls._last_refresh == 0:
            return 0
        return int(time.time() - cls._last_refresh)

    @classmethod
    def status(cls):
        return {
            "cached": cls._data is not None,
            "age_seconds": cls.age(),
            "ttl_seconds": cls._ttl_seconds
        }

def get_cached_cost():
    return CostSummaryCache.get()

def save_cached_cost(data):
    CostSummaryCache.set(data)