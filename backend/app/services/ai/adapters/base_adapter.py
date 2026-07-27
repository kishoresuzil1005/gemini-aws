"""Base Cloud Adapter — Phase 9"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.services.ai.orchestrator.models import Resource


class BaseCloudAdapter(ABC):
    provider_name: str = "base"

    @abstractmethod
    async def describe_resource(self, resource_id: str) -> Optional[Resource]:
        """Fetch a single resource by ID."""
        ...

    @abstractmethod
    async def list_resources(self, service: str, region: Optional[str] = None) -> List[Resource]:
        """List all resources for a given service."""
        ...

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check adapter connectivity and return status."""
        ...
