from typing import Dict, List, Type
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericResourceType, GenericAction
from app.providers.azure.capabilities import AzureCapabilities
from app.providers.gcp.capabilities import GCPCapabilities

class CapabilityRegistry:
    """Central registry answering: 'Can provider X perform action Y on resource Z?'"""
    
    def __init__(self):
        self._providers: Dict[CloudProvider, Any] = {
            CloudProvider.AZURE: AzureCapabilities,
            CloudProvider.GCP: GCPCapabilities,
            # We will migrate AWS capabilities here as well
        }
        
    def register_provider_capabilities(self, provider: CloudProvider, capability_class: Any):
        self._providers[provider] = capability_class

    def supports(self, provider: CloudProvider, resource: GenericResourceType, action: GenericAction) -> bool:
        cap_class = self._providers.get(provider)
        if not cap_class:
            # Default to False if capabilities matrix isn't defined yet
            return False
        return cap_class.supports(resource, action)

# Global registry
capability_registry = CapabilityRegistry()
