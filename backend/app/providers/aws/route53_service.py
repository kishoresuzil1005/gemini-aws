from typing import List, Dict, Any
from .aws_client import AWSClientManager

class Route53Service:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("route53")

    def list_hosted_zones(self) -> List[Dict[str, Any]]:
        response = self.client.list_hosted_zones()
        return response.get("HostedZones", [])
