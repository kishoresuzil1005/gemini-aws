"""CloudTrailProvider – placeholder for AWS CloudTrail event collection.

Status: ``not_implemented``

This provider implements the full :class:`~base_provider.BaseProvider` interface
so the pipeline runs unchanged when the implementation is added later.
Simply replace the body of :meth:`fetch` with the real CloudTrail calls.

Output key: ``events`` (will be added to AIContext in Phase 3)

Planned data shape::

    {
        "events": List[dict],   # raw CloudTrail event records
        "event_count": int,
        "look_back_hours": int,
    }
"""

import time
from typing import Any, Dict

from ..base_provider import BaseProvider
from ..common.constants import CLOUDTRAIL_PROVIDER_ENABLED, TTL_DYNAMIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource


class CloudTrailProvider(BaseProvider):
    """Placeholder – collects AWS CloudTrail events (Phase 3)."""

    name       = "cloudtrail"
    scope      = ProviderScope.DYNAMIC
    priority   = 70
    output_key = "events"
    cache_ttl  = TTL_DYNAMIC
    version    = "0.0"
    source     = "cloudtrail"
    enabled    = flag_enabled(CLOUDTRAIL_PROVIDER_ENABLED, default=False)

    def supports(self, level: ContextLevel) -> bool:
        return level == ContextLevel.DEEP

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        empty: Dict[str, Any] = {
            "events":          [],
            "event_count":     0,
            "look_back_hours": request.metrics_look_back,
        }
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(
            empty,
            status="not_implemented",
            enabled=False,
            execution_time_ms=exec_ms,
        )
