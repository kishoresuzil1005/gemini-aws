""" Agent — Phase 7"""
from __future__ import annotations
from typing import Any, Dict
from app.services.ai.investigation.session import InvestigationSession
from .base_agent import BaseAgent
import logging
logger = logging.getLogger(__name__)


class CostAgent(BaseAgent):
    name = "cost_agent"
    specialty = "cost"

    async def investigate(self, session: InvestigationSession, question: str) -> Dict[str, Any]:
        logger.info("[CostAgent] Investigating: %s", question)
        session.add_timeline("agent", "CostAgent investigating", {"question": question})
        return {"agent": self.name, "status": "pending_implementation", "question": question}
