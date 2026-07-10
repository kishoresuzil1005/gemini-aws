from typing import List, Dict, Any
from .aws_client import AWSClientManager

class EKSService:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("eks")

    def list_clusters(self) -> List[str]:
        response = self.client.list_clusters()
        return response.get("clusters", [])

    def describe_cluster(self, name: str) -> Dict[str, Any]:
        response = self.client.describe_cluster(name=name)
        return response.get("cluster", {})
