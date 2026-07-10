from azure.mgmt.network import NetworkManagementClient
from app.providers.azure.auth import AzureAuth
from app.providers.azure.models import AzureResourceMetadata
from app.providers.azure.exceptions import map_azure_exception
from typing import List

class NetworkDiscovery:
    def __init__(self, auth: AzureAuth, subscription_id: str):
        self.client = NetworkManagementClient(auth.credential, subscription_id)

    def list_virtual_networks(self) -> List[AzureResourceMetadata]:
        try:
            vnets = self.client.virtual_networks.list_all()
            return [
                AzureResourceMetadata(id=vnet.id, name=vnet.name, location=vnet.location, type=vnet.type)
                for vnet in vnets
            ]
        except Exception as e:
            raise map_azure_exception(e)
