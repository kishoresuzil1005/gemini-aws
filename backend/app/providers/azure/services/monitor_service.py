from azure.monitor.query import LogsQueryClient
from app.providers.azure.auth import AzureAuth
from app.providers.azure.exceptions import map_azure_exception

class MonitorService:
    def __init__(self, auth: AzureAuth):
        self.logs_client = LogsQueryClient(auth.credential)

    def execute(self, method_name: str, **kwargs):
        try:
            method = getattr(self.logs_client, method_name)
                
            res = method(**kwargs)
            return res
            
        except Exception as e:
            raise map_azure_exception(e)
