"""InventoryProvider – fetches inventory data using KnowledgeService."""

import time
import logging
from typing import Any, Dict

from ..base_provider import BaseProvider
from ..common.constants import INVENTORY_PROVIDER_ENABLED, TTL_STATIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)


class InventoryProvider(BaseProvider):
    """Fetches inventory context using KnowledgeService."""

    name       = "inventory"
    scope      = ProviderScope.STATIC
    priority   = 20
    output_key = "inventory"
    cache_ttl  = TTL_STATIC
    version    = "1.0"
    source     = "knowledge_service"
    enabled    = flag_enabled(INVENTORY_PROVIDER_ENABLED)

    def __init__(self, *, knowledge_client):
        super().__init__()
        self.knowledge_client = knowledge_client

    def supports(self, level: ContextLevel) -> bool:
        return True

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        try:
            data = self.knowledge_client.get_resource(resource.resource_id) or {}
        except Exception as exc:
            logger.debug("InventoryProvider lookup failed: %s", exc)
            data = {}
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)
