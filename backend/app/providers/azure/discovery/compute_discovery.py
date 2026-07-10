from azure.mgmt.compute import ComputeManagementClient
from app.providers.azure.auth import AzureAuth
from app.providers.azure.models import AzureResourceMetadata
from app.providers.azure.exceptions import map_azure_exception
from typing import List

class ComputeDiscovery:
    def __init__(self, auth: AzureAuth, subscription_id: str):
        self.client = ComputeManagementClient(auth.credential, subscription_id)

    def list_virtual_machines(self) -> List[AzureResourceMetadata]:
        try:
            vms = self.client.virtual_machines.list_all()
            return [
                AzureResourceMetadata(id=vm.id, name=vm.name, location=vm.location, type=vm.type)
                for vm in vms
            ]
        except Exception as e:
            raise map_azure_exception(e)
