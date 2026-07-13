from typing import List
from app.services.ai.assistant.knowledge_graph.query.graph_traversal import GraphTraversal

class ImpactEngine:
    """Answers 'What breaks?' based on downstream dependencies."""
    
    def __init__(self, traversal: GraphTraversal):
        self.traversal = traversal
        
    def get_impact(self, node_id: str) -> List[str]:
        # Implementation would traverse downstream edges looking for breaking conditions
        return [