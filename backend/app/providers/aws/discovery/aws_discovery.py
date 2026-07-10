from typing import Dict, Any, List
from .resource_discovery import ResourceDiscovery
from .relationship_discovery import RelationshipDiscovery
from .inventory_sync import InventorySync

class AWSDiscoveryEngine:
    """
    Main orchestrator for discovering all AWS infrastructure, building relationships, 
    and syncing it into the global Inventory and Knowledge Graph.
    """
    def __init__(self, client_manager):
        self.resource_discovery = ResourceDiscovery(client_manager)
        self.relationship_discovery = RelationshipDiscovery()
        self.inventory_sync = InventorySync()

    def run_full_discovery(self) -> Dict[str, Any]:
        print("[AWSDiscoveryEngine] Starting full AWS resource discovery...")
        
        # 1. Discover all raw resources
        raw_inventory = self.resource_discovery.discover_all()
        
        # 2. Build automated relationships (e.g. EC2 -> SG -> VPC)
        graph_nodes, graph_edges = self.relationship_discovery.build_graph(raw_inventory)
        
        # 3. Sync to persistent storage (DB and Knowledge Graph)
        sync_result = self.inventory_sync.sync_to_graph(graph_nodes, graph_edges)
        
        print("[AWSDiscoveryEngine] Discovery complete.")
        return {
            "status": "SUCCESS",
            "nodes_discovered": len(graph_nodes),
            "edges_built": len(graph_edges),
            "sync_details": sync_result
        }
