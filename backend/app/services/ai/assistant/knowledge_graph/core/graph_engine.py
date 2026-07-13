import networkx as nx
from typing import List, Optional, Dict
from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode, CloudEdge
import logging

logger = logging.getLogger(__name__)

class GraphEngine:
    """Core underlying graph wrapper powered by NetworkX."""
    
    def __init__(self):
        self._graph = nx.DiGraph()
        
    def add_node(self, node: CloudNode):
        self._graph.add_node(node.node_id, **node.model_dump())
        
    def add_edge(self, edge: CloudEdge):
        if not self._graph.has_node(edge.source_id):
            logger.warning(f"Adding edge source node implicitly: {edge.source_id}")
            self._graph.add_node(edge.source_id)
        if not self._graph.has_node(edge.target_id):
            logger.warning(f"Adding edge target node implicitly: {edge.target_id}")
            self._graph.add_node(edge.target_id)
            
        self._graph.add_edge(edge.source_id, edge.target_id, relationship=edge.relationship_type, **edge.properties)
        
    def get_node(self, node_id: str) -> Optional[CloudNode]:
        if self._graph.has_node(node_id):
            data = self._graph.nodes[node_id]
            # Build cloud node ignoring arbitrary extra kwargs for strictly the model
            return CloudNode(
                node_id=data.get("node_id", node_id),
                provider=data.get("provider", "unknown"),
                resource_type=data.get("resource_type", "unknown"),
                resource_name=data.get("resource_name", "unknown"),
                properties=data.get("properties", {})
            )
        return None
        
    def get_neighbors(self, node_id: str, direction: str = "both") -> List[str]:
        if not self._graph.has_node(node_id):
            return []
            
        if direction == "out":
            return list(self._graph.successors(node_id))
        elif direction == "in":
            return list(self._graph.predecessors(node_id))
        else:
            out_n = list(self._graph.successors(node_id))
            in_n = list(self._graph.predecessors(node_id))
            return list(set(out_n + in_n))
            
    def get_underlying_graph(self) -> nx.DiGraph:
        """Returns the raw networkx graph for advanced algorithms (e.g. shortest path) in traversal engines."""
        return self._grap