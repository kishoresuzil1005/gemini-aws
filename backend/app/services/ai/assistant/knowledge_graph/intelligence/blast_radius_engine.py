from typing import List, Dict
from app.services.ai.assistant.knowledge_graph.query.graph_traversal import GraphTraversal

class BlastRadiusEngine:
    """Determines the exact impact of changing or deleting a node."""
    
    def __init__(self, traversal: GraphTraversal):
        self.traversal = traversal
        
    def calculate_impact(self, target_node_id: str) -> Dict[str, any]:
        affected_nodes = self.traversal.get_blast_radius_subgraph(target_node_id)
        
        # In a full implementation, we'd weight this by criticality_engine.
        # For now we just return counts
        impact_score = len(affected_nodes) * 10
        criticality = "HIGH" if len(affected_nodes) > 5 else "LOW"
        
        return {
            "target": target_node_id,
            "affected_count": len(affected_nodes),
            "affected_nodes": affected_nodes,
            "impact_score": impact_score,
            "criticality": criticality
        }