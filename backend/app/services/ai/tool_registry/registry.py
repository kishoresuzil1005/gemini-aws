"""Tool Registry — Phase 3 / Phase 8"""
from __future__ import annotations
import logging
from typing import Dict, List, Optional, Type
from .base_tool import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    _instance: Optional["ToolRegistry"] = None
    _tools: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def get_instance(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, tool_class: Type[BaseTool]) -> None:
        self._tools[tool_class.name] = tool_class
        logger.info("[ToolRegistry] Registered: %s", tool_class.name)

    def get(self, name: str) -> Optional[Type[BaseTool]]:
        return self._tools.get(name)

    def instantiate(self, name: str) -> Optional[BaseTool]:
        cls = self._tools.get(name)
        return cls() if cls else None

    def list_tools(self) -> List[dict]:
        return [cls().schema() for cls in self._tools.values()]

    def clear(self) -> None:
        self._tools.clear()
