from typing import List, Optional
from app.services.ai.assistant.knowledge_graph.core.graph_engine import GraphEngine
from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode, CloudEdge

class GraphRepository:
    """
    Data Access Layer for the Graph.
    Ensures the rest of the platform isn't coupled to NetworkX or Neo4j directly.
    """
    
    def __init__(self, engine: GraphEngine):
        self.engine = engine
        
    def save_node(self, node: CloudNode):
        self.engine.add_node(node)
        
    def save_edge(self, edge: CloudEdge):
        self.engine.add_edge(edge)
        
    def find_node(self, node_id: str) -> Optional[CloudNode]:
        return self.engine.get_node(node_id)
        
    def get_neighbors(self, node_id: str) -> List[str]:
        return self.engine.get_neighbors(node_id)
        
    def clear(self):
        """Wipes the repository."""
        self.engine._graph.clear()
