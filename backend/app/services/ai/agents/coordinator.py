"""Coordinator Agent — Phase 7"""
from __future__ import annotations
import asyncio, logging
from typing import Any, Dict, List
from app.services.ai.investigation.session import InvestigationSession
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    Distributes investigation tasks across specialist agents.
    Runs them concurrently and merges findings.
    """

    def __init__(self, agents: List[BaseAgent]):
        self._agents = agents

    async def coordinate(self, session: InvestigationSession, question: str) -> Dict[str, Any]:
        tasks = [agent.investigate(session, question) for agent in self._agents if agent.can_handle(session.intent, [])]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        merged: Dict[str, Any] = {}
        for agent, result in zip(self._agents, results):
            if isinstance(result, Exception):
                logger.error("[Coordinator] Agent %s failed: %s", agent.name, result)
            else:
                merged[agent.name] = result
        return merged
