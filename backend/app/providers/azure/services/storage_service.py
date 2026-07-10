from azure.mgmt.storage import StorageManagementClient
from app.providers.azure.auth import AzureAuth
from app.providers.azure.exceptions import map_azure_exception

class StorageService:
    def __init__(self, auth: AzureAuth, subscription_id: str):
        self.client = StorageManagementClient(auth.credential, subscription_id)

    def execute(self, method_name: str, **kwargs):
        try:
            # We assume generic storage actions are directed to storage_accounts for now
            method = getattr(self.client.storage_accounts, method_name)
            
            res = method(**kwargs)
            if hasattr(res, "result"):
                return res.result()
            return res
            
        except Exception as e:
            raise map_azure_exception(e)
