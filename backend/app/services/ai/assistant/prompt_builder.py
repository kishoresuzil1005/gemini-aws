"""Prompt construction from the canonical AIContext model."""

import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

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
        print("========== PROMPT ==========")
        print(prompt)
        print("============================")
        return prompt, context_text
