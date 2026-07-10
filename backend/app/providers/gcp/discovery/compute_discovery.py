from google.cloud import compute_v1
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.models import GCPResourceMetadata
from app.providers.gcp.exceptions import map_gcp_exception
from typing import List

class ComputeDiscovery:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.client = compute_v1.InstancesClient(credentials=auth.credentials)

    def list_instances(self, project: str, zone: str) -> List[GCPResourceMetadata]:
        try:
            instances = self.client.list(project=project, zone=zone)
            return [
                GCPResourceMetadata(
                    id=str(instance.id),
                    name=instance.name,
                    zone_or_region=zone,
                    type="Instance",
                    project_id=project
                )
                for instance in instances
            ]
        except Exception as e:
            raise map_gcp_exception(e)
