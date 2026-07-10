from googleapiclient import discovery
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.models import GCPResourceMetadata
from app.providers.gcp.exceptions import map_gcp_exception
from typing import List

class SqlDiscovery:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.service = discovery.build('sqladmin', 'v1beta4', credentials=auth.credentials)

    def list_instances(self, project: str) -> List[GCPResourceMetadata]:
        try:
            req = self.service.instances().list(project=project)
            res = req.execute()
            items = res.get('items', [])
            return [
                GCPResourceMetadata(
                    id=item.get('name'),
                    name=item.get('name'),
                    zone_or_region=item.get('region'),
                    type="SqlInstance",
                    project_id=project
                )
                for item in items
            ]
        except Exception as e:
            raise map_gcp_exception(e)
