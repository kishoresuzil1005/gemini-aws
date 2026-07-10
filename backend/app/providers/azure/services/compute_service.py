from azure.mgmt.compute import ComputeManagementClient
from app.providers.azure.auth import AzureAuth
from app.providers.azure.exceptions import map_azure_exception

class ComputeService:
    def __init__(self, auth: AzureAuth, subscription_id: str):
        self.client = ComputeManagementClient(auth.credential, subscription_id)

    def execute(self, method_name: str, **kwargs):
        try:
            # e.g., method_name = "begin_deallocate"
            # kwargs = {"resource_group_name": "rg", "vm_name": "vm1"}
            method = getattr(self.client.virtual_machines, method_name)
            
            # These methods are often LRO (Long Running Operations)
            poller = method(**kwargs)
            if hasattr(poller, "result"):
                return poller.result()
            return poller
            
        except Exception as e:
            raise map_azure_exception(e)
