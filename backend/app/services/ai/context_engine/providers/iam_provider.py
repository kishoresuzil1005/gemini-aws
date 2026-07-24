"""IAMProvider – fetches IAM metadata (roles, policies, users) using KnowledgeService."""

import time
import logging
from typing import Any, Dict

from ..base_provider import BaseProvider
from ..common.constants import IAM_PROVIDER_ENABLED, TTL_DYNAMIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)


class IAMProvider(BaseProvider):
    """Fetches IAM context using KnowledgeService."""

    name       = "iam"
    scope      = ProviderScope.DYNAMIC
    priority   = 30
    output_key = "iam"
    cache_ttl  = TTL_DYNAMIC
    version    = "1.0"
    source     = "knowledge_service"
    enabled    = flag_enabled(IAM_PROVIDER_ENABLED)

    def __init__(self, *, knowledge_client):
        super().__init__()
        self.knowledge_client = knowledge_client

    def supports(self, level: ContextLevel) -> bool:
        return level in (ContextLevel.FULL, ContextLevel.DEEP)

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        data = self._fetch_iam(resource)
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)

    def _fetch_iam(self, resource: ResolvedResource) -> Dict[str, Any]:
        try:
            # KnowledgeService rules or direct relationships
            rels = self.knowledge_client.get_relationships(resource.resource_id)
            roles = [r.get("target") for r in rels if r.get("type") == "USES_ROLE"]
            return {
                "roles": roles,
                "policies": []
            }
        except Exception as exc:
            logger.debug("IAMProvider lookup failed: %s", exc)
            return {"roles": [], "policies": []}
