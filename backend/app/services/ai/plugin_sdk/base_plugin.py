"""Plugin Base Class — Phase 8"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.services.ai.orchestrator.models import ProviderResult, ProviderPriority


class BasePlugin(ABC):
    """Every third-party provider plugin must implement this interface."""
    name: str = "base_plugin"
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    priority: ProviderPriority = ProviderPriority.MEDIUM

    @abstractmethod
    async def run(self, question: str, session_id: Optional[str] = None, **kwargs) -> ProviderResult:
        """Execute the plugin and return a standardised ProviderResult."""
        ...

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "priority": self.priority,
        }
