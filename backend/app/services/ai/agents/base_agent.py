"""Base Agent — Phase 7"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.services.ai.investigation.session import InvestigationSession


class BaseAgent(ABC):
    name: str = "base_agent"
    specialty: str = "general"

    @abstractmethod
    async def investigate(self, session: InvestigationSession, question: str) -> Dict[str, Any]:
        """Run agent-specific investigation and return findings."""
        ...

    def can_handle(self, intent: str, service_hints: list) -> bool:
        """Return True if this agent is relevant for the given intent."""
        return True
