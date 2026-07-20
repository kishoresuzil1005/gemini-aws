import os
from datetime import datetime
from typing import Dict, Any

from .base_provider import BaseProvider
from .enums import ProviderScope, ContextLevel
from .resolved_resource import ResolvedResource
from .request import ContextRequest

class InventoryProvider(BaseProvider):
    """Collect inventory metadata for a resource.
    Returns a flat dictionary that maps to the ``inventory`` section of ``AIContext``.
    """

    name = "inventory"
    scope = ProviderScope.FULL
    priority = 0
    output_key = "inventory"
    enabled = os.getenv("ENABLE_INVENTORY_PROVIDER", "true").lower() == "true"

    def supports(self, level: ContextLevel) -> bool:
        # Inventory is useful for all levels.
        return True

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        # Stub – replace with real DB queries (PostgreSQL inventory tables).
        now = datetime.utcnow().isoformat()
        return {
            "resource_id": resource.resource_id,
            "account_id": "123456789012",
            "organization": "example-org",
            "environment": "prod",
            "project": "example-project",
            "discovery_time": now,
            "scanner_version": "v1.0",
            "last_discovered": now,
            "tags": [],
            "metadata": {},
            "owner": "team@example.com",
            "region": "us-east-1",
            "provider": "aws",
        }
