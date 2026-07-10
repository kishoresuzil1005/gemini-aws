import os
from google.oauth2 import service_account
from google.cloud import compute_v1

class GCPClientManager:
    """
    Centralized manager for GCP SDK clients.
    """
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        # Self-discovery of auth via GOOGLE_APPLICATION_CREDENTIALS

    def get_compute_client(self) -> compute_v1.InstancesClient:
        return compute_v1.InstancesClient()
