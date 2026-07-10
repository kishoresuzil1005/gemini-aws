from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode

class ResourceClassifier:
    """Automatically classifies resources without manual tags (e.g. EC2 -> App Server)."""
    
    def classify(self, node: CloudNode) -> str:
        if node.resource_type == "instance":
            # Simple heuristic
            if "db" in node.resource_name.lower():
                return "Database"
            return "Application Server"
        return "Unknown"
