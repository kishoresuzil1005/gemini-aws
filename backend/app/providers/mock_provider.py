from typing import Dict, Any
from app.providers.base_provider import BaseCloudProvider
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider

class MockCloudProvider(BaseCloudProvider):
    @property
    def name(self) -> CloudProvider:
        return CloudProvider.AWS

    def execute_action(self, action: str, resource_id: str, **kwargs) -> Dict[str, Any]:
        return {
            "status": "success",
            "action": action,
            "resource_id": resource_id,
            "message": "Mock execution successful",
            "metadata": kwargs
        }
