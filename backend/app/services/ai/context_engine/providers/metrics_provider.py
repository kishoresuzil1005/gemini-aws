"""MetricsProvider – fetches metrics using KnowledgeService."""

import time
import logging
from typing import Any, Dict

from ..base_provider import BaseProvider
from ..common.constants import METRICS_PROVIDER_ENABLED, TTL_DYNAMIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)


class MetricsProvider(BaseProvider):
    """Fetches metrics using KnowledgeService."""

    name       = "metrics"
    scope      = ProviderScope.DYNAMIC
    priority   = 60
    output_key = "metrics"
    cache_ttl  = TTL_DYNAMIC
    version    = "1.0"
    source     = "knowledge_service"
    enabled    = flag_enabled(METRICS_PROVIDER_ENABLED)

    def __init__(self, *, knowledge_client):
        super().__init__()
        self.knowledge_client = knowledge_client

    def supports(self, level: ContextLevel) -> bool:
        return level == ContextLevel.DEEP

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        data = {"summary": "Metrics are now provided via Knowledge Service rule evaluation."}
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)
