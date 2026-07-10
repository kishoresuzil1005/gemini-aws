from google.cloud import resourcemanager_v3
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.models import GCPResourceMetadata
from app.providers.gcp.exceptions import map_gcp_exception
from typing import List

class ResourceDiscovery:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.client = resourcemanager_v3.ProjectsClient(credentials=auth.credentials)

    def list_projects(self) -> List[GCPResourceMetadata]:
        try:
            projects = self.client.search_projects()
            return [
                GCPResourceMetadata(
                    id=p.name,
                    name=p.display_name,
                    zone_or_region="global",
                    type="Project",
                    project_id=p.project_id
                )
                for p in projects
            ]
        except Exception as e:
            raise map_gcp_exception(e)
