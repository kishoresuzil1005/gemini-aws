import json
from typing import Dict, Any, List

class ContextFilter:
    def __init__(self):
        pass

    def filter_graph_data(self, graph_data: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """
        Filters graph data based on the current intent.
        For example, if intent is SECURITY, only keep security group, IAM, and VPC data.
        """
        if not graph_data:
            return graph_data
            
        filtered = graph_data.copy()
        
        # Verbose metadata removal
        if "metadata" in filtered and intent not in ["INVENTORY", "DOCUMENTATION"]:
            if isinstance(filtered["metadata"], dict):
                filtered["metadata"] = {k: v for k, v in filtered["metadata"].items() if k in ["name", "arn", "region", "status"]}
                
        # If documentation, strip all relationships to save space
        if intent == "DOCUMENTATION":
            filtered.pop("relationships", None)
            filtered.pop("downstream", None)
            filtered.pop("upstream", None)
            
        return filtered

    def filter_tool_responses(self, tool_responses: List[Any], intent: str) -> List[Any]:
        """
        Filters tool responses to ensure we only include relevant ones based on intent.
        """
        filtered = []
        for response in tool_responses:
            tool_name = response.tool_name.lower()
            
            # Map tools to intent loosely
            if intent == "SECURITY" and "security" not in tool_name and "analysis" not in tool_name:
                continue
            if intent == "REMEDIATION" and "terraform" not in tool_name and "remediation" not in tool_name:
                continue
            if intent == "ORCHESTRATION" and "orchestrat" not in tool_name and "execute" not in tool_name:
                continue
            if intent == "DOCUMENTATION" and "doc" not in tool_name and "rag" not in tool_name and "search" not in tool_name:
                continue
                
            filtered.append(response)
            
        # Fallback: if we aggressively filtered everything, return original to avoid blanking out
        return filtered if filtered else tool_responses
