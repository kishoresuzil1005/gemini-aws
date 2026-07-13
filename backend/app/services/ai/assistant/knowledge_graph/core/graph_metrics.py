from typing import Dict
from app.services.ai.assistant.knowledge_graph.core.graph_repository import GraphRepository

class GraphMetrics:
    """Telemetry: node count, edge count, traversal time, query latency."""
    
    def __init__(self, repository: GraphRepository):
        self.repository = repository
        
    def get_stats(self) -> Dict[str, int]:
        graph = self.repository.engine.get_underlying_graph()
        return {
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges()
        }