import json
from typing import Dict, Any, List

class ContextFilter:
    def __init__(self):
        pass

    def filter_graph_data(self, graph_data: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """
        Filters graph data based on the current intent.
        For example, if intent is SECURITY, only keep security group, IAM, and VPC data.
        If intent is DEPENDENCY, keep upstream and downstream relationships.
        """
        if not graph_data:
            return graph_data
            
        # This is a naive implementation; in a real world scenario, 
        # this would filter based on actual graph schemas.
        filtered = graph_data.copy()
        
        # Example: removing verbose metadata if not needed
        if "metadata" in filtered and intent not in ["INVENTORY", "DOCUMENTATION"]:
            # Maybe keep only essential metadata
            if isinstance(filtered["metadata"], dict):
                filtered["metadata"] = {k: v for k, v in filtered["metadata"].items() if k in ["name", "arn", "region"]}
                
        return filtered

    def filter_tool_responses(self, tool_responses: List[Any], intent: str) -> List[Any]:
        """
        Filters tool responses to ensure we only include relevant ones.
        """
        # In this initial implementation, we trust the ToolRouter has only
        # provided relevant tool responses.
        return tool_responses
