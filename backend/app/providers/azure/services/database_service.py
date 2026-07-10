from azure.mgmt.sql import SqlManagementClient
from app.providers.azure.auth import AzureAuth
from app.providers.azure.exceptions import map_azure_exception

class DatabaseService:
    def __init__(self, auth: AzureAuth, subscription_id: str):
        self.client = SqlManagementClient(auth.credential, subscription_id)

    def execute(self, method_name: str, **kwargs):
        try:
            method = getattr(self.client.databases, method_name)
            
            res = method(**kwargs)
            if hasattr(res, "result"):
                return res.result()
            return res
            
        except Exception as e:
            raise map_azure_exception(e)
