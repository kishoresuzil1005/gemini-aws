from typing import List, Dict, Any
from .gcp_client import GCPClientManager

class GCPComputeService:
    def __init__(self, client_manager: GCPClientManager):
        self.client = client_manager.get_compute_client()
        self.project_id = client_manager.project_id

    def list_instances(self, zone: str = "us-central1-a") -> List[Dict[str, Any]]:
        print(f"[GCPComputeService] Discovering Compute Engine instances in {zone}...")
        instances = []
        try:
            request = {"project": self.project_id, "zone": zone}
            for instance in self.client.list(request=request):
                instances.append({"id": str(instance.id), "name": instance.name, "type": "GCP::Compute::Instance"})
        except Exception as e:
            print(f"[GCPComputeService] Skipping real API call, mock returning empty list due to: {e}")
        return instances
