import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

class AzureClientManager:
    """
    Centralized manager for Azure SDK clients using DefaultAzureCredential.
    """
    def __init__(self, subscription_id: str = None):
        self.subscription_id = subscription_id or os.getenv("AZURE_SUBSCRIPTION_ID")
        self.credential = DefaultAzureCredential()

    def get_compute_client(self) -> ComputeManagementClient:
        return ComputeManagementClient(self.credential, self.subscription_id)
