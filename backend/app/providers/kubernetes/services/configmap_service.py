from typing import Dict, Any, List, Optional
from app.providers.common.client_factory import client_factory

class ConfigmapService:
    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name
        # self.client = client_factory.get_kubernetes_client()

    def list(self, namespace: str = "default") -> List[Dict[str, Any]]:
        return []

    def get(self, name: str, namespace: str = "default") -> Optional[Dict[str, Any]]:
        return None

    def create(self, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        return {}

    def update(self, name: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        return {}

    def delete(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        return {"status": "deleted"}
