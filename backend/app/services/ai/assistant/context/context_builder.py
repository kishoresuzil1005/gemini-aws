import json
from typing import Dict, Any, List
from datetime import datetime, date

from app.services.ai.assistant.graph_retriever import GraphRetriever
from app.services.ai.assistant.assistant_models import ToolResponse, ConversationContext
from app.services.ai.assistant.context.context_filter import ContextFilter
from app.services.ai.assistant.context.context_compressor import ContextCompressor
from app.services.ai.assistant.context.context_prioritizer import ContextPrioritizer

MAX_CONTEXT_CHARS = 8000

def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)

def dict_to_text(d, indent=0):
    lines = []
    prefix = "  " * indent
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{prefix}{str(k).title()}:")
                lines.append(dict_to_text(v, indent + 1))
            elif v is not None and v != "":
                lines.append(f"{prefix}{str(k).title()}: {v}")
    elif isinstance(d, list):
        for item in d:
            if isinstance(item, (dict, list)):
                lines.append(dict_to_text(item, indent))
            elif item is not None and item != "":
                lines.append(f"{prefix}- {item}")
    else:
        if d is not None and d != "":
            lines.append(f"{prefix}{d}")
    return "\n".join(lines)

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
        
        # 1. Graph Section (only if intent warrants graph data)
        if ctx.current_resource and ctx.current_intent in ["SECURITY", "REMEDIATION", "ORCHESTRATION", "INVESTIGATION", "UNKNOWN"]:
            graph_data = self.graph_retriever.get_resource_context(ctx.current_resource)
            if graph_data:
                filtered_data = self.filter.filter_graph_data(graph_data, ctx.current_intent)
                compressed_data = self.compressor.compress(filtered_data)
                
                raw_sections.append({
                    "title": "RESOURCE GRAPH DATA",
                    "content": dict_to_text(compressed_data)
                })
        
        # 2. Tool Sections (Intent filtered context)
        filtered_responses = self.filter.filter_tool_responses(tool_responses, ctx.current_intent)
        for response in filtered_responses:
            raw_sections.append({
                "title": f"{response.tool_name.upper()} TOOL",
                "content": dict_to_text(response.context) if isinstance(response.context, (dict, list)) else str(response.context)
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
            formatted_sections.append(f"{sec['title']}\n{sec['content']}")
            
        final_context = "\n\n".join(formatted_sections)
        
        # Enforce size limit to prevent LLM Timeouts
        if len(final_context) > MAX_CONTEXT_CHARS:
            final_context = final_context[:MAX_CONTEXT_CHARS] + "\n...[CONTEXT TRUNCATED DUE TO SIZE LIMIT]"
            
        return final_context
