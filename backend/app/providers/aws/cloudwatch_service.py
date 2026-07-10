from typing import List, Dict, Any
from .aws_client import AWSClientManager

class CloudWatchService:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("cloudwatch")

    def describe_alarms(self) -> List[Dict[str, Any]]:
        response = self.client.describe_alarms()
        return response.get("MetricAlarms", [])

    def list_metrics(self, namespace: str) -> List[Dict[str, Any]]:
        response = self.client.list_metrics(Namespace=namespace)
        return response.get("Metrics", [])
