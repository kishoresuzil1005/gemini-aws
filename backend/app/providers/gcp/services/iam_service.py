from googleapiclient import discovery
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.exceptions import map_gcp_exception

class IamService:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.service = discovery.build('iam', 'v1', credentials=auth.credentials)

    def execute(self, method_name: str, **kwargs):
        try:
            # e.g. serviceAccounts().get()
            if hasattr(self.service.projects().serviceAccounts(), method_name):
                method = getattr(self.service.projects().serviceAccounts(), method_name)
                req = method(**kwargs)
                return req.execute()
            return {"status": "mock iam response"}
        except Exception as e:
            raise map_gcp_exception(e)
