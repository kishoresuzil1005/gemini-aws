from google.cloud import storage
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.models import GCPResourceMetadata
from app.providers.gcp.exceptions import map_gcp_exception
from typing import List

class StorageDiscovery:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.client = storage.Client(credentials=auth.credentials)

    def list_buckets(self, project: str) -> List[GCPResourceMetadata]:
        try:
            buckets = self.client.list_buckets(project=project)
            return [
                GCPResourceMetadata(
                    id=bucket.id,
                    name=bucket.name,
                    zone_or_region=bucket.location,
                    type="Bucket",
                    project_id=project
                )
                for bucket in buckets
            ]
        except Exception as e:
            raise map_gcp_exception(e)
