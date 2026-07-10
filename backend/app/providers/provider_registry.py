from typing import Dict, Optional, Callable
from app.providers.base_provider import BaseCloudProvider
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider

class ProviderRegistry:
    def __init__(self):
        # Store factories instead of instantiated objects
        self._provider_factories: Dict[CloudProvider, Callable[[], BaseCloudProvider]] = {}
        # Cache instantiated providers
        self._instantiated_providers: Dict[CloudProvider, BaseCloudProvider] = {}

    def register(self, provider_id: CloudProvider, factory: Callable[[], BaseCloudProvider]):
        self._provider_factories[provider_id] = factory

    def get_provider(self, name: CloudProvider) -> Optional[BaseCloudProvider]:
        if name in self._instantiated_providers:
            return self._instantiated_providers[name]
            
        factory = self._provider_factories.get(name)
        if factory:
            provider = factory()
            self._instantiated_providers[name] = provider
            return provider
            
        return None
