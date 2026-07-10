from google.cloud import compute_v1
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.models import GCPResourceMetadata
from app.providers.gcp.exceptions import map_gcp_exception
from typing import List

class NetworkDiscovery:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.client = compute_v1.NetworksClient(credentials=auth.credentials)

    def list_networks(self, project: str) -> List[GCPResourceMetadata]:
        try:
            networks = self.client.list(project=project)
            return [
                GCPResourceMetadata(
                    id=str(net.id),
                    name=net.name,
                    zone_or_region="global",
                    type="Network",
                    project_id=project
                )
                for net in networks
            ]
        except Exception as e:
            raise map_gcp_exception(e)
