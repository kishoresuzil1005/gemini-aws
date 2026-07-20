from enum import Enum
from typing import List


# Ordered list of context levels from lowest to highest.
# Used by ContextLevel.includes() for cumulative comparisons.
_LEVEL_ORDER: List[str] = ["basic", "standard", "full", "deep"]


class ContextLevel(str, Enum):
    """Cumulative context levels.

    Each level is a strict superset of those below it:

    * **BASIC**    – ResourceProvider + GraphProvider + InventoryProvider
    * **STANDARD** – BASIC + RelationshipAnalyzer
    * **FULL**     – STANDARD + IAMProvider + DocumentationProvider
    * **DEEP**     – FULL + MetricsProvider + CostProvider + Events providers
    """
    BASIC    = "basic"
    STANDARD = "standard"
    FULL     = "full"
    DEEP     = "deep"

    def includes(self, other: "ContextLevel") -> bool:
        """Return True if this level is equal to or higher than *other*.

        Example::

            ContextLevel.DEEP.includes(ContextLevel.BASIC)  # True
            ContextLevel.BASIC.includes(ContextLevel.DEEP)  # False
        """
        return _LEVEL_ORDER.index(self.value) >= _LEVEL_ORDER.index(other.value)


class ProviderScope(str, Enum):
    """Lifecycle classification for providers."""
    STATIC  = "static"   # slow-changing data; long TTL (30 min+)
    DYNAMIC = "dynamic"  # real-time data; short TTL (seconds to minutes)
