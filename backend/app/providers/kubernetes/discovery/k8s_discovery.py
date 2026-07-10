from typing import Dict, Any, List
from ..cluster_service import K8sClusterService

class K8sDiscoveryEngine:
    """
    Orchestrates discovery across all Kubernetes clusters.
    """
    def __init__(self, client_manager):
        self.cluster_service = K8sClusterService(client_manager)

    def run_full_discovery(self) -> Dict[str, Any]:
        print("[K8sDiscoveryEngine] Starting full Kubernetes discovery...")
        namespaces = ["default", "kube-system"]
        inventory = {"pods": [], "deployments": []}
        
        for ns in namespaces:
            inventory["pods"].extend(self.cluster_service.list_pods(ns))
            inventory["deployments"].extend(self.cluster_service.list_deployments(ns))
            
        return inventory
