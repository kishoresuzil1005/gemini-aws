from typing import Optional
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericActionRequest, TranslatedActionPayload
from app.services.ai.assistant.multicloud.provider_discovery import ProviderDiscovery
from app.services.ai.assistant.multicloud.provider_selector import ProviderSelector
from app.services.ai.assistant.multicloud.resource_mapper import ResourceMapper
from app.services.ai.assistant.multicloud.provider_capability import ProviderCapability
from app.services.ai.assistant.multicloud.action_translator import ActionTranslator

class MultiCloudEngine:
    """
    The orchestrator for Phase 7.1.
    Intercepts a generic request and translates it into a provider-specific payload.
    """
    def __init__(self):
        self.discovery = ProviderDiscovery()
        self.selector = ProviderSelector(self.discovery)
        self.mapper = ResourceMapper()
        self.capability = ProviderCapability()
        self.translator = ActionTranslator()

    def translate_request(self, request: GenericActionRequest, explicit_provider: Optional[CloudProvider] = None) -> TranslatedActionPayload:
        # 1. Select Provider
        provider = self.selector.select_provider(request, explicit_provider)
        
        # 2. Resource Mapping Validation
        _ = self.mapper.get_provider_resource_name(request.resource_type, provider)
        
        # 3. Capability Check
        self.capability.ensure_capability(provider, request.resource_type, request.action)
        
        # 4. Action Translation
        translated_payload = self.translator.translate(
            provider=provider,
            action=request.action,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            parameters=request.parameters
        )
        
        return translated_payload
