""" Cloud Adapter — Phase 9
Stub implementation. Connect real SDK calls here.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.services.ai.orchestrator.models import CloudProvider, Resource
from ..base_adapter import BaseCloudAdapter
import logging

logger = logging.getLogger(__name__)


class AzureAdapter(BaseCloudAdapter):
    provider_name = "azure"

    async def describe_resource(self, resource_id: str) -> Optional[Resource]:
        logger.info("[AzureAdapter] describe_resource: %s", resource_id)
        return None  # TODO: integrate Azure SDK

    async def list_resources(self, service: str, region: Optional[str] = None) -> List[Resource]:
        logger.info("[AzureAdapter] list_resources: service=%s region=%s", service, region)
        return []  # TODO: integrate Azure SDK

    async def health_check(self) -> Dict[str, Any]:
        return {"provider": "azure", "status": "stub", "message": "Not yet connected"}
