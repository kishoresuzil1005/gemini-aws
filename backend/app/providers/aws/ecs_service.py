from typing import List, Dict, Any
from .aws_client import AWSClientManager

class ECSService:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("ecs")

    def list_clusters(self) -> List[str]:
        response = self.client.list_clusters()
        return response.get("clusterArns", [])

    def list_services(self, cluster: str) -> List[str]:
        response = self.client.list_services(cluster=cluster)
        return response.get("serviceArns", [])
