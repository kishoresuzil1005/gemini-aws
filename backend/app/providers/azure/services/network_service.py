from azure.mgmt.network import NetworkManagementClient
from app.providers.azure.auth import AzureAuth
from app.providers.azure.exceptions import map_azure_exception

class NetworkService:
    def __init__(self, auth: AzureAuth, subscription_id: str):
        self.client = NetworkManagementClient(auth.credential, subscription_id)

    def execute(self, method_name: str, **kwargs):
        try:
            # We map generic network actions to virtual_networks
            method = getattr(self.client.virtual_networks, method_name)
            
            res = method(**kwargs)
            if hasattr(res, "result"):
                return res.result()
            return res
            
        except Exception as e:
            raise map_azure_exception(e)
