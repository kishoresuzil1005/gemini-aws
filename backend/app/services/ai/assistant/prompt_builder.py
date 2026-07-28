"""Prompt construction from the canonical AIContext model."""

import json
import logging
from typing import Any, Dict, List

from app.core.logging import get_logger, LogHelper
logger = get_logger(__name__)

from app.services.ai.assistant.context.prompt_templates import SYSTEM_PROMPT, build_user_prompt
from app.services.ai.context_engine.models import AIContext
from app.services.ai.assistant.reasoning.reasoning_models import ReasoningResult


class PromptBuilder:
    """Build the model messages without converting context in GraphAssistant."""

    MAX_CONTEXT_CHARS = 8000

    def build(
        self,
        *,
        question: str,
        history: str,
        context: AIContext,
        intent: str,
        reasoning: ReasoningResult | None = None,
    ) -> tuple[List[Dict[str, str]], str]:
        import time
        start_time = time.time()
        
        prompt_context = context.model_dump(exclude={"provider_data", "debug"})
        if reasoning:
            prompt_context["reasoning"] = reasoning.model_dump()
        context_text = json.dumps(
            prompt_context,
            default=str,
            indent=2,
        )
        if len(context_text) > self.MAX_CONTEXT_CHARS:
            context_text = context_text[:self.MAX_CONTEXT_CHARS] + "\n...[CONTEXT TRUNCATED]"

        prompt = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_user_prompt(question, history, context_text, intent),
            },
        ]
        
        duration_ms = (time.time() - start_time) * 1000
        chars = sum(len(m["content"]) for m in prompt)
        tokens = chars // 4
        
        sections = []
        if context.resource: sections.append("Inventory")
        if context.graph: sections.append("Graph")
        if context.security: sections.append("Security")
        if context.metrics: sections.append("Metrics")
        if context.cost: sections.append("Cost")
        if getattr(context, "documentation", None): sections.append("Documentation")
        if getattr(context, "recommendations", None): sections.append("Recommendations")
        
        LogHelper.summary("Prompt Summary", {
            "Sections Included": sections or ["None"],
            "Prompt Size": f"{chars / 1024:.1f} KB",
            "Characters": chars,
            "Estimated Tokens": tokens,
            "Duration": f"{duration_ms:.1f} ms"
        })
        
        # Log actual prompt only in debug
        logger.debug(f"Prompt:\n{prompt}")
        
        return prompt, context_text
