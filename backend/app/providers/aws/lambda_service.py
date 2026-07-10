from typing import List, Dict, Any
from .aws_client import AWSClientManager

class LambdaService:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("lambda")

    def list_functions(self) -> List[Dict[str, Any]]:
        response = self.client.list_functions()
        return response.get("Functions", [])

    def get_function(self, function_name: str) -> Dict[str, Any]:
        return self.client.get_function(FunctionName=function_name)
