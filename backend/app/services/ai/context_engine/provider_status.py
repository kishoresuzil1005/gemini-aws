from enum import Enum

class ProviderStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    TIMEOUT = "timeout"
    DISABLED = "disabled"
    INVALID_RESPONSE = "invalid_response"
