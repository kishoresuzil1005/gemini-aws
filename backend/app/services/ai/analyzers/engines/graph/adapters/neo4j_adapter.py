"""
Mock Neo4j Adapter.
Converts Neo4j dictionary responses into the standard InfrastructureGraph.
"""
from typing import Dict, Any, List
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph
from app.services.ai.analyzers.engines.graph.graph_processor import GraphProcessor

class Neo4jAdapter:
    """Adapter to convert Neo4j dictionary topology into InfrastructureGraph."""
    
    @classmethod
    def fetch_graph(cls, neo4j_payload: Dict[str, Any]) -> InfrastructureGraph:
        """
        Neo4j payload typically has 'nodes' and 'edges'.
        """
        raw_nodes = neo4j_payload.get("nodes", [])
        raw_edges = neo4j_payload.get("edges", [])
        
        # We pass it to the GraphProcessor to validate, repair, and normalize
        return GraphProcessor.process(raw_nodes, raw_edges)
