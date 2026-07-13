from typing import Dict, Any
from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode

class OwnershipEngine:
    """Determines ownership based on tags, IAM, namespaces, or labels."""
    
    def get_owner(self, node: CloudNode) -> str:
        tags = node.properties.get("tags", {})
        owner = tags.get("Owner") or tags.get("Team")
        if owner:
            return owner
        
        # Kubernetes fallback
        if node.provider == "KUBERNETES":
            labels = node.properties.get("labels", {})
            return labels.get("app.kubernetes.io/managed-by", "UNKNOWN")
            
        return "UNKNOWN"