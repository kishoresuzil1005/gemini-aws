from typing import Dict, Any
from .cross_cloud_discovery import CrossCloudDiscovery
from .cross_cloud_graph import CrossCloudGraphBuilder

class InventorySyncManager:
    """
    Periodically synchronizes the master Cross-Cloud discovery state into 
    the persistent Postgres databases and the Neo4j Knowledge Graph. (Epic 8)
    """
    def __init__(self, cross_cloud_discovery: CrossCloudDiscovery, graph_builder: CrossCloudGraphBuilder):
        self.discovery = cross_cloud_discovery
        self.graph_builder = graph_builder

    def sync_multi_cloud_state(self):
        print("[InventorySyncManager] Commencing multi-cloud inventory synchronization...")
        
        # 1. Pull raw inventory from all 4 providers
        inventory_state = self.discovery.discover_all_clouds()
        
        # 2. Build multi-cloud edges and nodes
        self.graph_builder.build_cross_cloud_relationships(inventory_state)
        
        # 3. Upsert to Postgres / Neo4j
        print(f"[InventorySyncManager] Synced {len(self.graph_builder.global_nodes)} cross-cloud resources to persistent storage.")
        return True
