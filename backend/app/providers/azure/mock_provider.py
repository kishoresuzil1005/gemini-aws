from typing import Dict, Any
from app.providers.base_provider import BaseCloudProvider
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider

class AzureMockProvider(BaseCloudProvider):
    @property
    def name(self) -> CloudProvider:
        return CloudProvider.AZURE

    def execute_action(self, action: str, resource_id: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "message": f"Azure executed {action} on {resource_id}"}
