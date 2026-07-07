import json
from typing import Dict, Any, List
from app.services.ai.assistant.graph_retriever import GraphRetriever
from app.services.ai.assistant.assistant_models import ToolResponse, ConversationContext
from datetime import datetime, date

def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)

class ContextBuilder:
    def __init__(self):
        self.graph_retriever = GraphRetriever()

    def build_structured_context(self, ctx: ConversationContext, tool_responses: List[ToolResponse]) -> str:
        """
        Creates structured context sections (Inventory, Graph, Tool Outputs)
        rather than flat concatenation.
        """
        sections = []
        
        # 1. Graph Section
        if ctx.current_resource:
            graph_data = self.graph_retriever.get_resource_context(ctx.current_resource)
            if graph_data:
                sections.append("### Neo4j Graph Properties ###")
                sections.append(json.dumps(graph_data, indent=2, default=json_serializer))
        
        # 2. Tool Sections
        for response in tool_responses:
            sections.append(f"### {response.tool_name} Output ###")
            sections.append(json.dumps(response.context, indent=2, default=json_serializer))
            
        if not sections:
            sections.append("No specific resource target identified in the query. Provide general CloudOps assistance.")
            
        return "\n\n".join(sections)
