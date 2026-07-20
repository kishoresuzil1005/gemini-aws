from enum import Enum

class ProviderStatus(str, Enum):
    """The standard status used across the entire Context Engine."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
