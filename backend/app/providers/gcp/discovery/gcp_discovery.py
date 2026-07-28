from app.core.logging import get_logger
logger = get_logger(__name__)
from typing import Dict, Any, List
from ..compute_service import GCPComputeService

class GCPDiscoveryEngine:
    """
    Orchestrates discovery across all GCP projects and zones.
    """
    def __init__(self, client_manager):
        self.compute = GCPComputeService(client_manager)

    def run_full_discovery(self) -> Dict[str, Any]:
        logger.debug("[GCPDiscoveryEngine] Starting full GCP discovery...")
        inventory = {
            "compute_instances": self.compute.list_instances()
        }
        return inventory
