""" Cloud Adapter — Phase 9
Stub implementation. Connect real SDK calls here.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.services.ai.orchestrator.models import CloudProvider, Resource
from ..base_adapter import BaseCloudAdapter
import logging

logger = logging.getLogger(__name__)


class KubernetesAdapter(BaseCloudAdapter):
    provider_name = "k8s"

    async def describe_resource(self, resource_id: str) -> Optional[Resource]:
        logger.info("[KubernetesAdapter] describe_resource: %s", resource_id)
        return None  # TODO: integrate Kubernetes SDK

    async def list_resources(self, service: str, region: Optional[str] = None) -> List[Resource]:
        logger.info("[KubernetesAdapter] list_resources: service=%s region=%s", service, region)
        return []  # TODO: integrate Kubernetes SDK

    async def health_check(self) -> Dict[str, Any]:
        return {"provider": "k8s", "status": "stub", "message": "Not yet connected"}
