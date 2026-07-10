from google.cloud import compute_v1
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.exceptions import map_gcp_exception
from app.providers.gcp.operation_tracker import OperationTracker

class ComputeService:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.client = compute_v1.InstancesClient(credentials=auth.credentials)

    def execute(self, method_name: str, **kwargs):
        try:
            method = getattr(self.client, method_name)
            
            # e.g., method_name = "stop", kwargs = {"project": "p", "zone": "z", "instance": "i"}
            operation = method(**kwargs)
            
            # Wait for operation
            result = OperationTracker.wait_for_operation(
                self.client, 
                operation, 
                project=kwargs.get("project"),
                zone=kwargs.get("zone")
            )
            return result
        except Exception as e:
            raise map_gcp_exception(e)
