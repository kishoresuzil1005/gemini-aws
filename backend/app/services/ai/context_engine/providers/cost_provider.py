"""CostProvider – fetches cost data using KnowledgeService."""

import time
import logging
from typing import Any, Dict

from ..base_provider import BaseProvider
from ..common.constants import COST_PROVIDER_ENABLED, TTL_DYNAMIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)


class CostProvider(BaseProvider):
    """Fetches cost context using KnowledgeService."""

    name       = "cost"
    scope      = ProviderScope.DYNAMIC
    priority   = 70
    output_key = "cost"
    cache_ttl  = TTL_DYNAMIC
    version    = "1.0"
    source     = "knowledge_service"
    enabled    = flag_enabled(COST_PROVIDER_ENABLED)

    def __init__(self, *, knowledge_client):
        super().__init__()
        self.knowledge_client = knowledge_client

    def supports(self, level: ContextLevel) -> bool:
        return level == ContextLevel.DEEP

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        
        try:
            cost_rules = self.knowledge_client.get_rules(category="cost")
            data = {"cost_rules": cost_rules}
        except Exception as exc:
            logger.debug("CostProvider lookup failed: %s", exc)
            data = {"cost_rules": []}
            
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)
