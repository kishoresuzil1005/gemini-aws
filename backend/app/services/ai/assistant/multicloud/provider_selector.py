from typing import Optional
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericActionRequest
from app.services.ai.assistant.multicloud.provider_discovery import ProviderDiscovery

class ProviderNotFoundError(Exception):
    pass

class ProviderSelector:
    """Selects the correct CloudProvider based on intent, taxonomy inference, or context."""
    
    def __init__(self, discovery: ProviderDiscovery):
        self.discovery = discovery

    def select_provider(self, request: GenericActionRequest, explicit_provider: Optional[CloudProvider] = None) -> CloudProvider:
        """
        Determines the destination provider.
        Priority 1: Explicit provider passed in context.
        Priority 2: Inference from taxonomy (simplified here).
        Priority 3: Default fallback.
        """
        # 1. Explicit override
        if explicit_provider:
            if not self.discovery.is_provider_connected(explicit_provider):
                raise ProviderNotFoundError(f"Explicit provider {explicit_provider} is not connected.")
            return explicit_provider
            
        # 2. Taxonomy Inference (simplified rule-based)
        # E.g., if target string contains specific keywords
        resource_id_lower = request.resource_id.lower()
        if "arn:aws" in resource_id_lower or "i-" in resource_id_lower:
            return CloudProvider.AWS
        if "/subscriptions/" in resource_id_lower or "azure" in resource_id_lower:
            return CloudProvider.AZURE
        if "projects/" in resource_id_lower or "gcp" in resource_id_lower:
            return CloudProvider.GCP
            
        # 3. Default fallback for testing
        if self.discovery.is_provider_connected(CloudProvider.AWS):
            return CloudProvider.AWS
            
        raise ProviderNotFoundError("Could not determine a connected Cloud Provider for the request.")
