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
