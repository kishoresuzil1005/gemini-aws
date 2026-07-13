from typing import List
from app.services.ai.assistant.knowledge_graph.history.graph_snapshot import GraphSnapshot

class GraphTimeline:
    """Provides a chronological view of changes to the infrastructure."""
    
    def __init__(self):
        self.snapshots: List[GraphSnapshot] = []
        
    def get_timeline(self):
        return self.snapshot