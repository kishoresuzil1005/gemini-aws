from typing import List, Dict, Any
from .aws_client import AWSClientManager

class SecretsManagerService:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("secretsmanager")

    def list_secrets(self) -> List[Dict[str, Any]]:
        response = self.client.list_secrets()
        return response.get("SecretList", [])
