"""HealthProvider – placeholder for AWS Health / Trusted Advisor events.

Status: ``not_implemented``

Planned data shape::

    {
        "events":            List[dict],   # open health events
        "trusted_advisor":   List[dict],   # Trusted Advisor check results
        "service_status":    str,
    }
"""

import time
from typing import Any, Dict

from ..base_provider import BaseProvider
from ..common.constants import HEALTH_PROVIDER_ENABLED, TTL_DYNAMIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource


class HealthProvider(BaseProvider):
    """Placeholder – collects AWS Health and Trusted Advisor events (Phase 3)."""

    name       = "health"
    scope      = ProviderScope.DYNAMIC
    priority   = 100
    output_key = "health"
    cache_ttl  = TTL_DYNAMIC
    version    = "0.0"
    source     = "aws_health"
    enabled    = flag_enabled(HEALTH_PROVIDER_ENABLED, default=False)

    def supports(self, level: ContextLevel) -> bool:
        return level == ContextLevel.DEEP

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        empty: Dict[str, Any] = {
            "events":          [],
            "trusted_advisor": [],
            "service_status":  "unknown",
        }
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(
            empty,
            status="not_implemented",
            enabled=False,
            execution_time_ms=exec_ms,
        )
