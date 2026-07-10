from typing import List, Dict, Any
from .aws_client import AWSClientManager

class VPCService:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("ec2")

    def describe_vpcs(self) -> List[Dict[str, Any]]:
        response = self.client.describe_vpcs()
        return response.get("Vpcs", [])

    def describe_subnets(self) -> List[Dict[str, Any]]:
        response = self.client.describe_subnets()
        return response.get("Subnets", [])

    def describe_security_groups(self) -> List[Dict[str, Any]]:
        response = self.client.describe_security_groups()
        return response.get("SecurityGroups", [])
