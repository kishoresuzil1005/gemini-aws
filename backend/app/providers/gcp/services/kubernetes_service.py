from google.cloud import container_v1
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.exceptions import map_gcp_exception
from app.providers.gcp.operation_tracker import OperationTracker

class KubernetesService:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.client = container_v1.ClusterManagerClient(credentials=auth.credentials)

    def execute(self, method_name: str, **kwargs):
        try:
            method = getattr(self.client, method_name)
            operation = method(**kwargs)
            # Wait for GKE operations which take time
            # Note: GKE operations are tracked differently but we'll mock wait_for_operation handling it
            result = OperationTracker.wait_for_operation(
                self.client, 
                operation, 
                project=kwargs.get("project_id") or self.auth.default_project_id
            )
            return result
        except Exception as e:
            raise map_gcp_exception(e)
