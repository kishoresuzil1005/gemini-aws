from typing import List
from app.services.ai.assistant.llm.base_provider import BaseProvider
from app.services.ai.assistant.prompt_templates import SYSTEM_PROMPT, build_user_prompt
from app.services.ai.assistant.assistant_models import ChatResponse, ToolResponse

class ResponseGenerator:
    def __init__(self, provider: BaseProvider):
        self.provider = provider

    def generate(self, question: str, history_str: str, context_str: str, intent: str, target: str, tool_responses: List[ToolResponse], request_id: str, stream: bool = False) -> ChatResponse:
        prompt = build_user_prompt(question, history_str, context_str, intent)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        answer = self.provider.generate_response(messages=messages, request_id=request_id, stream=stream)
        
        # Determine sources
        sources = ["Neo4j Knowledge Graph"] if target else []
        for tr in tool_responses:
            sources.append(tr.tool_name)
            
        return ChatResponse(
            answer=answer,
            intent=intent,
            resource=target,
            sources=sources
        )
