import json
from typing import Dict, Any, List
from datetime import datetime, date

from app.services.ai.assistant.graph_retriever import GraphRetriever
from app.services.ai.assistant.assistant_models import ToolResponse, ConversationContext
from app.services.ai.assistant.context.context_filter import ContextFilter
from app.services.ai.assistant.context.context_compressor import ContextCompressor
from app.services.ai.assistant.context.context_prioritizer import ContextPrioritizer

def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)

class ContextBuilder:
    def __init__(self):
        self.graph_retriever = GraphRetriever()
        self.filter = ContextFilter()
        self.compressor = ContextCompressor()
        self.prioritizer = ContextPrioritizer()

    def build_structured_context(self, ctx: ConversationContext, tool_responses: List[ToolResponse], memory_context: str = "") -> str:
        """
        Creates structured, prioritized, and compressed context sections.
        """
        raw_sections = []
        
        # 1. Graph Section
        if ctx.current_resource:
            graph_data = self.graph_retriever.get_resource_context(ctx.current_resource)
            if graph_data:
                # Filter and compress
                filtered_data = self.filter.filter_graph_data(graph_data, ctx.current_intent)
                compressed_data = self.compressor.compress(filtered_data)
                
                raw_sections.append({
                    "title": "RESOURCE GRAPH DATA",
                    "content": json.dumps(compressed_data, indent=2, default=json_serializer)
                })
        
        # 2. Tool Sections
        filtered_responses = self.filter.filter_tool_responses(tool_responses, ctx.current_intent)
        for response in filtered_responses:
            raw_sections.append({
                "title": f"{response.tool_name.upper()} TOOL",
                "content": json.dumps(response.context, indent=2, default=json_serializer)
            })
            
        # 3. Memory Section
        if memory_context:
            raw_sections.append({
                "title": "CONVERSATION MEMORY",
                "content": memory_context
            })
            
        if not raw_sections:
            return "No specific resource target identified in the query. Provide general CloudOps assistance."
            
        # Prioritize and format
        prioritized_sections = self.prioritizer.prioritize_sections(raw_sections)
        
        formatted_sections = []
        for sec in prioritized_sections:
            formatted_sections.append(f"==========================\n{sec['title']}\n==========================\n{sec['content']}")
            
        return "\n\n".join(formatted_sections)
