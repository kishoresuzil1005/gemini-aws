"""
Core Infrastructure Graph definition.
This is the central topology storage agnostic to any data source.
"""
from typing import Dict, List, Any
from pydantic import BaseModel, Field

class InfrastructureGraph(BaseModel):
    """
    Pure data structure representing the cloud/CMDB topology.
    Does NOT contain traversal logic.
    """
    nodes: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Map of node ID to properties.")
    edges: List[Dict[str, Any]] = Field(default_factory=list, description="List of edges: source, target, type.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Graph-level metadata (e.g., extraction time).")

    @classmethod
    def version(cls) -> str:
        """Returns the current semantic version of this engine component."""
        return "1.0.0"

    def get_node(self, node_id: str) -> Dict[str, Any]:
        return self.nodes.get(node_id, {})

    def has_node(self, node_id: str) -> bool:
        """Returns True if the node exists in the topology."""
        return node_id in self.nodes

    def neighbors(self, node_id: str) -> List[str]:
        """Returns all nodes connected by an outbound edge."""
        return [e["target"] for e in self.edges if e.get("source") == node_id]

    def parents(self, node_id: str) -> List[str]:
        """Returns all nodes connected by an inbound edge."""
        return [e["source"] for e in self.edges if e.get("target") == node_id]

    def children(self, node_id: str) -> List[str]:
        """Alias for neighbors, returns downstream dependencies."""
        return self.neighbors(node_id)

    # -------------------------------------------------------------
    # Enterprise Graph Helpers (Phase 2)
    # -------------------------------------------------------------
    
    def find_resource_by_id(self, node_id: str) -> Dict[str, Any]:
        return self.get_node(node_id)
        
    def find_resources_by_type(self, rtype: str, index: Any = None) -> List[Dict[str, Any]]:
        if index and hasattr(index, "by_type"):
            return [self.get_node(n) for n in index.by_type.get(rtype, set()) if self.has_node(n)]
        return [n for n in self.nodes.values() if n.get("type", n.get("resource_type")) == rtype]
        
    def find_resources_by_region(self, region: str, index: Any = None) -> List[Dict[str, Any]]:
        if index and hasattr(index, "by_region"):
            return [self.get_node(n) for n in index.by_region.get(region, set()) if self.has_node(n)]
        return [n for n in self.nodes.values() if n.get("region", "global") == region]
        
    def find_resources_by_account(self, account: str, index: Any = None) -> List[Dict[str, Any]]:
        if index and hasattr(index, "by_account"):
            return [self.get_node(n) for n in index.by_account.get(account, set()) if self.has_node(n)]
        return [n for n in self.nodes.values() if n.get("account_id", n.get("account", "unknown")) == account]
        
    def find_resources_by_tag(self, key: str, value: str, index: Any = None) -> List[Dict[str, Any]]:
        if index and hasattr(index, "by_tag"):
            tag_map = index.by_tag.get(key, {})
            return [self.get_node(n) for n in tag_map.get(str(value), set()) if self.has_node(n)]
        return [n for n in self.nodes.values() if str(n.get("tags", {}).get(key)) == str(value)]
        
    def find_root_nodes(self, index: Any = None) -> List[str]:
        """Nodes with out-edges but no in-edges."""
        roots = []
        for nid in self.nodes.keys():
            in_deg = len(index.reverse_adjacency.get(nid, set())) if index else len(self.parents(nid))
            out_deg = len(index.adjacency.get(nid, set())) if index else len(self.neighbors(nid))
            if in_deg == 0 and out_deg > 0:
                roots.append(nid)
        return roots
        
    def find_leaf_nodes(self, index: Any = None) -> List[str]:
        """Nodes with in-edges but no out-edges."""
        leaves = []
        for nid in self.nodes.keys():
            in_deg = len(index.reverse_adjacency.get(nid, set())) if index else len(self.parents(nid))
            out_deg = len(index.adjacency.get(nid, set())) if index else len(self.neighbors(nid))
            if in_deg > 0 and out_deg == 0:
                leaves.append(nid)
        return leaves
        
    def find_isolated_nodes(self, index: Any = None) -> List[str]:
        """Nodes with no edges."""
        isolated = []
        for nid in self.nodes.keys():
            in_deg = len(index.reverse_adjacency.get(nid, set())) if index else len(self.parents(nid))
            out_deg = len(index.adjacency.get(nid, set())) if index else len(self.neighbors(nid))
            if in_deg == 0 and out_deg == 0:
                isolated.append(nid)
        return isolated
