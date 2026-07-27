"""Tool Planner — Phase 3"""
from __future__ import annotations
import logging
from typing import List
from app.services.ai.orchestrator.models import ReasoningResult
from app.services.ai.reasoning_engine.rule_set import required_providers
from .registry import ToolRegistry

logger = logging.getLogger(__name__)


class ToolPlanner:
    """
    Given a ReasoningResult, selects the minimal set of tools/providers needed.
    Avoids calling Cost provider for security questions, etc.
    """
    def __init__(self):
        self._registry = ToolRegistry.get_instance()

    def plan(self, reasoning: ReasoningResult) -> List[str]:
        providers = required_providers(
            intent=reasoning.intent.value,
            service_hints=reasoning.resource_query.service_hints,
        )
        logger.info("[ToolPlanner] Planned providers: %s for intent=%s", providers, reasoning.intent)
        return providers
