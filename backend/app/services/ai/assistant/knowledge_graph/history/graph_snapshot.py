from app.services.ai.assistant.knowledge_graph.core.graph_repository import GraphRepository
from datetime import datetime

class GraphSnapshot:
    """Captures a point-in-time snapshot of the Knowledge Graph."""
    
    def take_snapshot(self, repository: GraphRepository, timestamp: datetime = None):
        pas