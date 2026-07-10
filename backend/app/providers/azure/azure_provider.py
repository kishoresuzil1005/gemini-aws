from typing import Dict, Any
from app.providers.base_provider import BaseCloudProvider
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericResourceType
from app.providers.azure.auth import AzureAuth
from app.providers.azure.services.compute_service import ComputeService
from app.providers.azure.services.storage_service import StorageService
from app.providers.azure.services.network_service import NetworkService
from app.providers.azure.services.database_service import DatabaseService
from app.providers.azure.services.identity_service import IdentityService
from app.providers.azure.services.monitor_service import MonitorService
from app.providers.azure.discovery.resource_discovery import ResourceDiscovery
from app.providers.azure.response_normalizer import AzureResponseNormalizer
from app.providers.azure.translator import AzureTranslator

class AzureProvider(BaseCloudProvider):
    def __init__(self, subscription_id: str = "mock-sub-id"):
        # For a real integration, the sub_id would be injected or read from environment
        self.subscription_id = subscription_id
        self.auth = AzureAuth()
        
        self.compute = ComputeService(self.auth, self.subscription_id)
        self.storage = StorageService(self.auth, self.subscription_id)
        self.network = NetworkService(self.auth, self.subscription_id)
        self.database = DatabaseService(self.auth, self.subscription_id)
        self.identity = IdentityService(self.auth, self.subscription_id)
        self.monitor = MonitorService(self.auth)
        self.discovery = ResourceDiscovery(self.auth, self.subscription_id)

    @property
    def name(self) -> CloudProvider:
        return CloudProvider.AZURE

    def execute_action(self, action: str, resource_id: str, **kwargs) -> Dict[str, Any]:
        """
        The generic entrypoint from the MultiCloud engine.
        MultiCloudEngine will pass the generic resource_type in kwargs to route to the correct Azure service.
        """
        try:
            # We expect MultiCloudEngine to pass `generic_resource_type` for routing
            # Alternatively, action_translator could prepend it to the api_call, but passing it as kwarg is cleaner
            res_type = kwargs.pop("generic_resource_type", None)
            
            # Apply Azure-specific translation logic
            # ActionTranslator may have provided vm_name, but we might need rg_name, etc.
            # However, since we bypassed AzureTranslator, let's call it here
            from app.services.ai.assistant.multicloud.multicloud_models import TranslatedActionPayload
            payload = TranslatedActionPayload(provider=self.name, api_call=action, payload={"resource_id": resource_id, **kwargs})
            method_name, final_kwargs = AzureTranslator().translate(payload)
            
            if res_type == GenericResourceType.COMPUTE:
                raw_response = self.compute.execute(method_name, **final_kwargs)
            elif res_type == GenericResourceType.STORAGE:
                raw_response = self.storage.execute(action, **kwargs)
            elif res_type == GenericResourceType.NETWORK:
                raw_response = self.network.execute(action, **kwargs)
            elif res_type == GenericResourceType.DATABASE:
                raw_response = self.database.execute(action, **kwargs)
            elif res_type == GenericResourceType.IDENTITY:
                raw_response = self.identity.execute(action, **kwargs)
            else:
                raw_response = {"status": "success", "message": f"Azure Executed {action} on {resource_id} (Unmapped Service)"}
                
            return AzureResponseNormalizer.normalize(raw_response).model_dump()
            
        except Exception as e:
            return AzureResponseNormalizer.normalize_error(str(e)).model_dump()
