from azure.mgmt.resource.resources import ResourceManagementClient
from app.providers.azure.auth import AzureAuth
from app.providers.azure.models import AzureResourceMetadata
from app.providers.azure.exceptions import map_azure_exception
from typing import List

class ResourceDiscovery:
    def __init__(self, auth: AzureAuth, subscription_id: str):
        self.client = ResourceManagementClient(auth.credential, subscription_id)

    def discover_resources(self, resource_group_name: str = None) -> List[AzureResourceMetadata]:
        try:
            if resource_group_name:
                resources = self.client.resources.list_by_resource_group(resource_group_name)
            else:
                resources = self.client.resources.list()
                
            return [
                AzureResourceMetadata(id=res.id, name=res.name, location=res.location, type=res.type)
                for res in resources
            ]
        except Exception as e:
            raise map_azure_exception(e)
