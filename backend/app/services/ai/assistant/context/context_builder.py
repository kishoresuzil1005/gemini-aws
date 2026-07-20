import json
from typing import Dict, Any, List, Optional
from datetime import datetime, date

from app.services.ai.assistant.graph_retriever import GraphRetriever
from app.services.ai.assistant.assistant_models import ConversationContext
from app.services.ai.assistant.reasoning.reasoning_models import ReasoningResult
from app.services.ai.assistant.actions.action_models import ActionResult
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

    def build_structured_context(
        self,
        conversation_context: ConversationContext,
        reasoning_result: Optional[ReasoningResult] = None,
        action_result: Optional[ActionResult] = None,
        memory_context: Optional[str] = None
    ) -> str:
        """
        Creates structured, prioritized, and compressed context sections.
        """
        raw_sections = []
        ctx = conversation_context
        
        # 1. AI Context Engine Section
        if ctx.current_resource and ctx.current_intent in ["SECURITY", "REMEDIATION", "ORCHESTRATION", "INVESTIGATION", "UNKNOWN", "DEPENDENCY", "BLAST_RADIUS"]:
            from app.services.ai.context_engine.engine import ContextEngine
            from app.services.ai.context_engine.request import ContextRequest
            from app.services.ai.context_engine.enums import ContextLevel
            import asyncio
            
            try:
                engine = ContextEngine()
                req = ContextRequest(
                    identifier=ctx.current_resource,
                    level=ContextLevel.DEEP
                )
                # Run the context engine
                ai_context = asyncio.run(engine.build_context(req))
                
                # Append ContextEngine outputs
                if ai_context.graph:
                    raw_sections.append({
                        "title": "RESOURCE GRAPH DATA",
                        "content": dict_to_text(ai_context.graph)
                    })
                
                if ai_context.findings:
                    for analyzer_name, analyzer_findings in ai_context.findings.items():
                        raw_sections.append({
                            "title": f"FINDINGS: {analyzer_name.upper()}",
                            "content": dict_to_text(analyzer_findings)
                        })
                        
                if ai_context.recommendations:
                    raw_sections.append({
                        "title": "RECOMMENDATIONS",
                        "content": dict_to_text(ai_context.recommendations)
                    })
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"ContextEngine failed: {e}")
        
        # 2. Reasoning Sections
        if reasoning_result and reasoning_result.findings:
            for finding in reasoning_result.findings:
                raw_sections.append({
                    "title": f"FINDING: {finding.source_tool.upper()}",
                    "content": dict_to_text(finding.raw_data) if isinstance(finding.raw_data, (dict, list)) else str(finding.raw_data)
                })
                
        if reasoning_result and reasoning_result.risks:
            risk_texts = []
            for risk in reasoning_result.risks:
                risk_texts.append(f"- [{risk.severity}] {risk.description} (Score: {risk.score})")
            raw_sections.append({
                "title": "PRIORITIZED RISKS",
                "content": "\n".join(risk_texts)
            })
            
        if reasoning_result and reasoning_result.conflicts:
            conflict_texts = []
            for conflict in reasoning_result.conflicts:
                status = "RESOLVED" if conflict.resolved else "UNRESOLVED"
                conflict_texts.append(f"- [{status}] {conflict.description} (Winner: {conflict.winner})")
            raw_sections.append({
                "title": "CONFLICTS",
                "content": "\n".join(conflict_texts)
            })
            
        if reasoning_result and reasoning_result.explanation:
            raw_sections.append({
                "title": "REASONING EXPLANATION",
                "content": reasoning_result.explanation
            })
            
        # 5. Add Action Result
        if action_result:
            sections = [f"## Operational Action Result"]
            sections.append(f"Status: {action_result.status}")
            sections.append(f"Action Completed: {action_result.action_completed}")
            sections.append(f"Rollback Available: {action_result.rollback_created}")
            sections.append(f"Message: {action_result.user_message}")
            if action_result.dry_run:
                sections.append(f"Dry Run Impact: {action_result.dry_run.summary}")
            if action_result.execution_result and action_result.execution_result.error:
                sections.append(f"Error: {action_result.execution_result.error}")
            raw_sections.append({
                "title": "OPERATIONAL ACTION",
                "content": "\n".join(sections)
            })

        # 6. Add Relevant Memory
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