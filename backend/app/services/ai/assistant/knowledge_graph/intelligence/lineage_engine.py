from typing import Dict, Any
from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode

class LineageEngine:
    """Tracks how a resource was created (Terraform, Manual, CloudFormation)."""
    
    def get_lineage(self, node: CloudNode) -> str:
        tags = node.properties.get("tags", {})
        
        if "aws:cloudformation:stack-name" in tags:
            return "CloudFormation"
            
        if tags.get("ManagedBy") == "Terraform":
            return "Terraform"
            
        return "Manual