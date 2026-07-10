from azure.mgmt.storage import StorageManagementClient
from app.providers.azure.auth import AzureAuth
from app.providers.azure.models import AzureResourceMetadata
from app.providers.azure.exceptions import map_azure_exception
from typing import List

class StorageDiscovery:
    def __init__(self, auth: AzureAuth, subscription_id: str):
        self.client = StorageManagementClient(auth.credential, subscription_id)

    def list_storage_accounts(self) -> List[AzureResourceMetadata]:
        try:
            accounts = self.client.storage_accounts.list()
            return [
                AzureResourceMetadata(id=acc.id, name=acc.name, location=acc.location, type=acc.type)
                for acc in accounts
            ]
        except Exception as e:
            raise map_azure_exception(e)
