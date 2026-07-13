from typing import Dict, Any, List, Optional
from app.providers.common.client_factory import client_factory

class AksService:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        # Client would typically be obtained via client_factory.get_azure_client(..., credential)
        # self.client = client_factory.get_azure_client("aks")

    def list(self) -> List[Dict[str, Any]]:
        return []

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        return None

    def create(self, **kwargs) -> Dict[str, Any]:
        return {}

    def update(self, resource_id: str, **kwargs) -> Dict[str, Any]:
        return {}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        return {"status": "deleted"}
