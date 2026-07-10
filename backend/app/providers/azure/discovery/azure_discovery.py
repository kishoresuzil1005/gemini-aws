from typing import Dict, Any, List
from ..compute_service import AzureComputeService

class AzureDiscoveryEngine:
    """
    Orchestrates discovery across all Azure resource groups.
    """
    def __init__(self, client_manager):
        self.compute = AzureComputeService(client_manager)
        # self.network = AzureNetworkService(client_manager)
        # self.storage = AzureStorageService(client_manager)

    def run_full_discovery(self) -> Dict[str, Any]:
        print("[AzureDiscoveryEngine] Starting full Azure discovery...")
        inventory = {
            "virtual_machines": self.compute.list_virtual_machines()
        }
        return inventory
