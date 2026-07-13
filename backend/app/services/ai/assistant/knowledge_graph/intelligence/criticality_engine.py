from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode

class CriticalityEngine:
    """Derives whether a node is Production, Dev, or Mission Critical."""
    
    @staticmethod
    def get_criticality(node: CloudNode) -> str:
        # Simple heuristic based on tags/properties
        tags = node.properties.get("tags", {})
        env = tags.get("Environment", "unknown").lower()
        
        if env in ["prod", "production"]:
            return "MISSION_CRITICAL"
        if env in ["dev", "development", "test"]:
            return "LOW_PRIORITY"
            
        return "UNKNOWN"