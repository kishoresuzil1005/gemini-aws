"""ProviderRegistry – central registry of provider instances.

Providers are registered during application startup.  The registry reads
feature‑flag environment variables (defined in :mod:`common.constants`)
and silently skips any provider whose flag is disabled.

Usage::

    from context_engine.registry import registry
    from context_engine.providers import GraphProvider

    registry.register(GraphProvider())
    providers = registry.ordered_providers  # sorted by priority
"""

import logging
from typing import Dict, List, Optional

from .base_provider import BaseProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Singleton registry that holds provider *instances* sorted by priority."""

    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider) -> None:
        """Register *provider* unless its ``enabled`` flag is ``False``.

        Parameters
        ----------
        provider:
            An instantiated provider.  Must have a unique ``name``.
        """
        if not provider.enabled:
            logger.debug("Provider %r is disabled (feature flag). Skipping.", provider.name)
            return
        if provider.name in self._providers:
            logger.warning("Provider %r already registered. Overwriting.", provider.name)
        self._providers[provider.name] = provider
        logger.debug("Registered provider %r (priority=%d).", provider.name, provider.priority)

    def get(self, name: str) -> Optional[BaseProvider]:
        """Return the provider with the given *name*, or ``None``."""
        return self._providers.get(name)

    def unregister(self, name: str) -> None:
        """Remove a provider by name (useful in tests)."""
        self._providers.pop(name, None)

    def clear(self) -> None:
        """Remove all registered providers."""
        self._providers.clear()

    @property
    def ordered_providers(self) -> List[BaseProvider]:
        """Return providers sorted by ``priority`` ascending (lower = earlier)."""
        return sorted(self._providers.values(), key=lambda p: p.priority)

    def __len__(self) -> int:
        return len(self._providers)

    def __repr__(self) -> str:
        names = [p.name for p in self.ordered_providers]
        return f"<ProviderRegistry providers={names}>"


# ---------------------------------------------------------------------------
#  Global singleton
# ---------------------------------------------------------------------------
registry = ProviderRegistry()


def register_default_providers() -> None:
    """Register all built‑in providers respecting their feature flags.

    Call this once during application startup (e.g., in the FastAPI lifespan
    event or the app factory).
    """
    from .providers import (
        ResourceProvider,
        GraphProvider,
        InventoryProvider,
        IAMProvider,
        DocumentationProvider,
        MetricsProvider,
        CostProvider,
        CloudTrailProvider,
        EventBridgeProvider,
        ConfigProvider,
        HealthProvider,
    )

    for provider_cls in [
        ResourceProvider,
        GraphProvider,
        InventoryProvider,
        IAMProvider,
        DocumentationProvider,
        MetricsProvider,
        CostProvider,
        CloudTrailProvider,
        EventBridgeProvider,
        ConfigProvider,
        HealthProvider,
    ]:
        registry.register(provider_cls())
