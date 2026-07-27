"""Base Tool Interface — Phase 3 / Phase 8"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ToolInput(BaseModel):
    resource_id: Optional[str] = None
    question: str = ""
    session_id: Optional[str] = None
    parameters: Dict[str, Any] = {}


class ToolOutput(BaseModel):
    tool_name: str
    success: bool
    data: Dict[str, Any] = {}
    error: Optional[str] = None
    latency_ms: int = 0


class BaseTool(ABC):
    """Every registered AI tool must implement this interface."""
    name: str = "base_tool"
    description: str = ""
    requires_approval: bool = False

    @abstractmethod
    async def execute(self, input: ToolInput) -> ToolOutput:
        """Execute the tool and return structured output."""
        ...

    def schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "requires_approval": self.requires_approval,
        }
