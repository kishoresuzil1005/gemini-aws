from typing import List, Dict, Any
from .aws_client import AWSClientManager

class IAMService:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("iam")

    def list_users(self) -> List[Dict[str, Any]]:
        response = self.client.list_users()
        return response.get("Users", [])

    def list_roles(self) -> List[Dict[str, Any]]:
        response = self.client.list_roles()
        return response.get("Roles", [])

    def list_policies(self) -> List[Dict[str, Any]]:
        response = self.client.list_policies(Scope='Local')
        return response.get("Policies", [])
