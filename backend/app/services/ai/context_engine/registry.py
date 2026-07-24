"""ProviderRegistry – central registry of provider instances.

Providers are registered during application startup.
All providers now rely entirely on the Enterprise Knowledge Service
instead of direct provider logic (boto3, postgres, neo4j, etc).
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
        if not provider.enabled:
            logger.debug("Provider %r is disabled (feature flag). Skipping.", provider.name)
            return
        if provider.name in self._providers:
            logger.warning("Provider %r already registered. Overwriting.", provider.name)
        self._providers[provider.name] = provider
        logger.debug("Registered provider %r (priority=%d).", provider.name, provider.priority)

    def get(self, name: str) -> Optional[BaseProvider]:
        return self._providers.get(name)

    def unregister(self, name: str) -> None:
        self._providers.pop(name, None)

    def clear(self) -> None:
        self._providers.clear()

    @property
    def ordered_providers(self) -> List[BaseProvider]:
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
    """Register all built‑in providers respecting their feature flags."""
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

    from .service_container import ServiceContainer

    container = ServiceContainer.instance()

    registry.register(ResourceProvider(
        knowledge_client=container.knowledge_client
    ))
    
    registry.register(GraphProvider(
        knowledge_client=container.knowledge_client
    ))
    
    registry.register(InventoryProvider(
        knowledge_client=container.knowledge_client
    ))
    
    registry.register(IAMProvider(
        knowledge_client=container.knowledge_client
    ))
    
    registry.register(DocumentationProvider(
        knowledge_client=container.knowledge_client
    ))
    
    registry.register(MetricsProvider(
        knowledge_client=container.knowledge_client
    ))
    
    registry.register(CostProvider(
        knowledge_client=container.knowledge_client
    ))

    # Placeholders without external dependencies
    registry.register(CloudTrailProvider())
    registry.register(EventBridgeProvider())
    registry.register(ConfigProvider())
    registry.register(HealthProvider())
