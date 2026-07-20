import os
from typing import Dict, Any
from .base_provider import BaseProvider
from .enums import ProviderScope, ContextLevel
from .resolved_resource import ResolvedResource
from .request import ContextRequest
from .common.constants import RESOURCE_PROVIDER_ENABLED
from .common.helpers import flag_enabled

class ResourceProvider(BaseProvider):
    """Provides basic resource metadata.
    Output is placed under the ``resource`` section of ``AIContext``.
    """

    name = "resource"
    scope = ProviderScope.FULL
    priority = 0
    output_key = "resource"
    enabled = flag_enabled(RESOURCE_PROVIDER_ENABLED)

    def supports(self, level: ContextLevel) -> bool:
        # Resource metadata is useful for all levels.
        return True

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        # Minimal stub – returns basic identifiers.
        return self._build_response(
            {
                "resource_id": resource.resource_id,
                "resource_name": getattr(resource, "resource_name", ""),
                "resource_type": getattr(resource, "resource_type", ""),
                "provider": getattr(resource, "provider", ""),
                "region": getattr(resource, "region", ""),
                "account_id": getattr(resource, "account_id", ""),
                "arn": getattr(resource, "arn", ""),
                "status": getattr(resource, "status", ""),
                "original_identifier": resource.original_identifier,
            }
        )
