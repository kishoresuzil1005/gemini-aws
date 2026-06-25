from datetime import datetime, timedelta
from threading import Lock


class EC2Cache:

    _summary_cache = {}
    _extended_cache = {}

    CACHE_DURATION = timedelta(minutes=5)
    _lock = Lock()

    @classmethod
    def get_summary(cls, region: str):

        with cls._lock:
            cache = cls._summary_cache.get(region)

            if not cache:
                return None

            if datetime.utcnow() > cache["expires"]:
                del cls._summary_cache[region]
                return None

            return cache["data"]

    @classmethod
    def set_summary(cls, region: str, data):

        with cls._lock:
            cls._summary_cache[region] = {
                "data": data,
                "expires": datetime.utcnow() + cls.CACHE_DURATION
            }

    @classmethod
    def get_extended(cls, region: str):

        with cls._lock:
            cache = cls._extended_cache.get(region)

            if not cache:
                return None

            if datetime.utcnow() > cache["expires"]:
                del cls._extended_cache[region]
                return None

            return cache["data"]

    @classmethod
    def set_extended(cls, region: str, data):

        with cls._lock:
            cls._extended_cache[region] = {
                "data": data,
                "expires": datetime.utcnow() + cls.CACHE_DURATION
            }

    @classmethod
    def clear_region(cls, region: str):

        with cls._lock:
            cls._summary_cache.pop(region, None)
            cls._extended_cache.pop(region, None)

    @classmethod
    def clear_all(cls):

        with cls._lock:
            cls._summary_cache.clear()
            cls._extended_cache.clear()

