import os
from typing import Dict, Any
from .base_provider import BaseProvider
from .enums import ProviderScope, ContextLevel
from .resolved_resource import ResolvedResource
from .request import ContextRequest

class ResourceProvider(BaseProvider):
    """Provides basic resource metadata.
    Output is placed under the ``resource`` section of ``AIContext``.
    """

    name = "resource"
    scope = ProviderScope.FULL
    priority = 0
    output_key = "resource"
    enabled = os.getenv("ENABLE_RESOURCE_PROVIDER", "true").lower() == "true"

    def supports(self, level: ContextLevel) -> bool:
        # Resource metadata is useful for all levels.
        return True

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        # Minimal stub – returns basic identifiers.
        return {
            "id": resource.resource_id,
            "original_identifier": resource.original_identifier,
        }
