"""
Graph Metrics.
Computes standard topological metrics (Degree, Centrality, etc.) in O(1) using GraphIndex.
"""
from typing import List, Set
from app.services.ai.analyzers.engines.graph.graph_index import GraphIndex

class GraphMetrics:
    
    @classmethod
    def version(cls) -> str:
        return "1.0.0"

    @staticmethod
    def in_degree(index: GraphIndex, node_id: str) -> int:
        """Returns the number of inbound edges."""
        return len(index.reverse_adjacency.get(node_id, set()))

    @staticmethod
    def out_degree(index: GraphIndex, node_id: str) -> int:
        """Returns the number of outbound edges."""
        return len(index.adjacency.get(node_id, set()))

    @staticmethod
    def is_leaf(index: GraphIndex, node_id: str) -> bool:
        """True if the node has no outbound dependencies."""
        return GraphMetrics.out_degree(index, node_id) == 0

    @staticmethod
    def is_root(index: GraphIndex, node_id: str) -> bool:
        """True if the node has no inbound dependencies."""
        return GraphMetrics.in_degree(index, node_id) == 0
