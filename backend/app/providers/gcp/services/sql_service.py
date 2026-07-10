from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.exceptions import map_gcp_exception

# Using the google-api-python-client for Cloud SQL admin as it's common
from googleapiclient import discovery

class SqlService:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.service = discovery.build('sqladmin', 'v1beta4', credentials=auth.credentials)

    def execute(self, method_name: str, **kwargs):
        try:
            # A bit of logic to route dynamic method calls
            if hasattr(self.service.instances(), method_name):
                method = getattr(self.service.instances(), method_name)
                request = method(**kwargs)
                return request.execute()
            return {"status": "mock sql response"}
        except Exception as e:
            raise map_gcp_exception(e)
