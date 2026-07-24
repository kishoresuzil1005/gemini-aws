"""DocumentationProvider – fetches internal docs using KnowledgeService."""

import time
import logging
from typing import Any, Dict

from ..base_provider import BaseProvider
from ..common.constants import DOCS_PROVIDER_ENABLED, TTL_STATIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)


class DocumentationProvider(BaseProvider):
    """Fetches internal documentation context using KnowledgeService."""

    name       = "documentation"
    scope      = ProviderScope.STATIC
    priority   = 50
    output_key = "documentation"
    cache_ttl  = TTL_STATIC
    version    = "1.0"
    source     = "knowledge_service"
    enabled    = flag_enabled(DOCS_PROVIDER_ENABLED)

    def __init__(self, *, knowledge_client):
        super().__init__()
        self.knowledge_client = knowledge_client

    def supports(self, level: ContextLevel) -> bool:
        return level in (ContextLevel.FULL, ContextLevel.DEEP)

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        try:
            # Query KS for rules related to this resource
            rules = self.knowledge_client.get_rules()
            data = {"related_rules": rules}
        except Exception as exc:
            logger.debug("DocumentationProvider lookup failed: %s", exc)
            data = {"related_rules": []}
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)
