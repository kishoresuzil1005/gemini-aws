from google.cloud import compute_v1
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.exceptions import map_gcp_exception

class NetworkService:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.client = compute_v1.NetworksClient(credentials=auth.credentials)

    def execute(self, method_name: str, **kwargs):
        try:
            method = getattr(self.client, method_name)
            return method(**kwargs)
        except Exception as e:
            raise map_gcp_exception(e)
