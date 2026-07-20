"""ConfigProvider – placeholder for AWS Config resource‑configuration snapshots.

Status: ``not_implemented``

Planned data shape::

    {
        "configuration_items": List[dict],
        "compliance_status":   str,
        "rules_evaluated":     int,
    }
"""

import time
from typing import Any, Dict

from ..base_provider import BaseProvider
from ..common.constants import CONFIG_PROVIDER_ENABLED, TTL_DYNAMIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource


class ConfigProvider(BaseProvider):
    """Placeholder – collects AWS Config snapshots (Phase 3)."""

    name       = "config"
    scope      = ProviderScope.DYNAMIC
    priority   = 90
    output_key = "compliance"
    cache_ttl  = TTL_DYNAMIC
    version    = "0.0"
    source     = "aws_config"
    enabled    = flag_enabled(CONFIG_PROVIDER_ENABLED, default=False)

    def supports(self, level: ContextLevel) -> bool:
        return level == ContextLevel.DEEP

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        empty: Dict[str, Any] = {
            "configuration_items": [],
            "compliance_status":   "unknown",
            "rules_evaluated":     0,
        }
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(
            empty,
            status="not_implemented",
            enabled=False,
            execution_time_ms=exec_ms,
        )
