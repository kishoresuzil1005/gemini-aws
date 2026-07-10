from google.cloud import storage
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.exceptions import map_gcp_exception

class StorageService:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.client = storage.Client(credentials=auth.credentials, project=auth.default_project_id)

    def execute(self, method_name: str, **kwargs):
        try:
            # We map generic storage actions to buckets
            if "bucket_name" in kwargs:
                bucket = self.client.bucket(kwargs.pop("bucket_name"))
                method = getattr(bucket, method_name)
                return method(**kwargs)
            else:
                method = getattr(self.client, method_name)
                return method(**kwargs)
        except Exception as e:
            raise map_gcp_exception(e)
