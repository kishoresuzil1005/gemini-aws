from enum import Enum

class ProviderStatus(str, Enum):
    """The standard status used across the entire Context Engine."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"
    DISABLED = "disabled"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
