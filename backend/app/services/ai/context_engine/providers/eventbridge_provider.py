"""EventBridgeProvider – placeholder for AWS EventBridge event collection.

Status: ``not_implemented``

Implements the full :class:`~base_provider.BaseProvider` interface so the
pipeline runs unchanged when the real fetch is added.

Planned data shape::

    {
        "rules":   List[dict],   # matching EventBridge rules
        "events":  List[dict],   # recent matched events
    }
"""

import time
from typing import Any, Dict

from ..base_provider import BaseProvider
from ..common.constants import EVENTBRIDGE_PROVIDER_ENABLED, TTL_DYNAMIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource


class EventBridgeProvider(BaseProvider):
    """Placeholder – collects AWS EventBridge rules and events (Phase 3)."""

    name       = "eventbridge"
    scope      = ProviderScope.DYNAMIC
    priority   = 80
    output_key = "events"
    cache_ttl  = TTL_DYNAMIC
    version    = "0.0"
    source     = "eventbridge"
    enabled    = flag_enabled(EVENTBRIDGE_PROVIDER_ENABLED, default=False)

    def supports(self, level: ContextLevel) -> bool:
        return level == ContextLevel.DEEP

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        empty: Dict[str, Any] = {"rules": [], "events": []}
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(
            empty,
            status="not_implemented",
            enabled=False,
            execution_time_ms=exec_ms,
        )
