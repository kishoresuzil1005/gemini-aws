import json
from typing import Dict, Any
from app.services.ai.assistant.graph_retriever import GraphRetriever
from app.services.ai.assistant.tool_router import ToolRouter

class ContextBuilder:
    def __init__(self):
        self.graph_retriever = GraphRetriever()
        self.tool_router = ToolRouter()

    def build_context(self, intent_data: Dict[str, Any]) -> str:
        """
        Gathers Neo4j graph data and tool outputs into a single prompt context string.
        """
        target_resource = intent_data.get("target_resource")
        intent = intent_data.get("intent", "UNKNOWN")
        
        context_parts = []
        
        if target_resource:
            graph_data = self.graph_retriever.get_resource_context(target_resource)
            if graph_data:
                context_parts.append("### Neo4j Graph Properties ###")
                context_parts.append(json.dumps(graph_data, indent=2))
                
            tool_data = self.tool_router.route(intent, target_resource)
            if tool_data:
                context_parts.append(f"### {intent} Analysis ###")
                context_parts.append(json.dumps(tool_data, indent=2))
                
        else:
            context_parts.append("No specific resource target identified in the query. Provide general CloudOps assistance.")
            
        return "\n\n".join(context_parts)
