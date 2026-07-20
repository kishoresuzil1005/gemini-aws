"""Abstract base class for all AI Context Engine providers.

Every concrete provider must:
* Set class attributes: ``name``, ``scope``, ``priority``, ``output_key``, ``enabled``, ``version``, ``source``.
* Implement :meth:`supports` to indicate which :class:`~enums.ContextLevel` values it handles.
* Implement :meth:`fetch` and return a response built with :meth:`_build_response`.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .enums import ContextLevel, ProviderScope
from .request import ContextRequest
from .resolved_resource import ResolvedResource


class BaseProvider(ABC):
    """Base class for all providers.

    Concrete providers must set:

    Attributes
    ----------
    name : str
        Unique identifier (e.g. ``"graph"``).
    scope : ProviderScope
        ``STATIC`` or ``DYNAMIC``.
    priority : int
        Execution order – lower runs first. Default ``0``.
    output_key : str | None
        Top‑level field on :class:`~models.AIContext` where the provider's
        ``data`` will be stored.
    enabled : bool
        Whether the provider is active. Read from a feature‑flag env var.
    cache_ttl : int | None
        Seconds to cache the result. ``None`` disables caching.
    version : str
        Provider schema version string (e.g. ``"1.0"``).
    source : str
        Data source label for debugging (e.g. ``"neo4j"``, ``"cloudwatch"``).
    """

    name: str
    scope: ProviderScope
    priority: int = 0
    output_key: Optional[str] = None
    enabled: bool = True
    cache_ttl: Optional[int] = None
    version: str = "1.0"
    source: str = "unknown"

    def supports(self, level: ContextLevel) -> bool:
        """Return ``True`` if this provider should run for *level*."""
        raise NotImplementedError

    @abstractmethod
    async def fetch(
        self,
        resource: ResolvedResource,
        request: ContextRequest,
    ) -> Dict[str, Any]:
        """Fetch raw data for *resource* and return a standardized response.

        Always build the return value with :meth:`_build_response` so that every
        provider produces a consistent ``{"metadata": {...}, "data": {...}}`` shape.
        """
        ...

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------

    def _build_response(
        self,
        data: Dict[str, Any],
        *,
        status: str = "ok",
        enabled: bool = True,
        execution_time_ms: float = 0.0,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build the standardized provider response envelope.

        Parameters
        ----------
        data:
            The raw collected data to place under the ``data`` key.
        status:
            ``"ok"`` for successful fetches; ``"not_implemented"`` for stubs;
            ``"error"`` when the fetch partially failed.
        enabled:
            Whether the provider is live (``False`` for placeholder providers).
        execution_time_ms:
            Wall‑clock time taken to execute ``fetch``, in milliseconds.
        extra_metadata:
            Any additional fields to merge into the ``metadata`` block.
        """
        metadata: Dict[str, Any] = {
            "provider": self.name,
            "version": self.version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "cache_ttl": self.cache_ttl,
            "status": status,
            "enabled": enabled,
            "execution_time_ms": round(execution_time_ms, 3),
            "source": self.source,
        }
        if extra_metadata:
            metadata.update(extra_metadata)
        return {"metadata": metadata, "data": data}

    def _not_implemented_response(self, empty_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convenience method for placeholder providers."""
        return self._build_response(empty_data, status="not_implemented", enabled=False)
