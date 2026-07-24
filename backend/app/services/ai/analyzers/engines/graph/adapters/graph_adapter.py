"""
Offline Graph Adapter.
Converts graph dictionary responses into the standard InfrastructureGraph.
"""
from typing import Dict, Any, List
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph
from app.services.ai.analyzers.engines.graph.graph_processor import GraphProcessor

class GraphAdapter:
    """Adapter to convert standard dictionary topology into InfrastructureGraph."""
    
    @classmethod
    def fetch_graph(cls, graph_payload: Dict[str, Any]) -> InfrastructureGraph:
        """
        Graph payload typically has 'nodes' and 'edges'.
        """
        raw_nodes = graph_payload.get("nodes", [])
        raw_edges = graph_payload.get("edges", [])
        
        # We pass it to the GraphProcessor to validate, repair, and normalize
        return GraphProcessor.process(raw_nodes, raw_edges)
