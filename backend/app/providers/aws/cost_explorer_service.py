from typing import List, Dict, Any
from .aws_client import AWSClientManager

class CostExplorerService:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("ce")

    def get_cost_and_usage(self, start_date: str, end_date: str) -> Dict[str, Any]:
        response = self.client.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )
        return response
