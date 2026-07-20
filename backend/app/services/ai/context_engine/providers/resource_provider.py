"""ResourceProvider – fetches core resource metadata from PostgreSQL.

Queries the ``resources`` table (ResourceDB) and falls back to the
``resource_nodes`` table if the main record is missing.  Falls back to
Neo4j MemoryGraphStore when the DB is unreachable.
"""

import json
import time
import logging
from typing import Any, Dict, Optional

from ..base_provider import BaseProvider
from ..common.constants import RESOURCE_PROVIDER_ENABLED, TTL_STATIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)


class ResourceProvider(BaseProvider):
    """Fetches core resource identity metadata from the PostgreSQL inventory."""

    name       = "resource"
    scope      = ProviderScope.STATIC
    priority   = 0
    output_key = "resource"
    cache_ttl  = TTL_STATIC
    version    = "1.0"
    source     = "postgres"
    enabled    = flag_enabled(RESOURCE_PROVIDER_ENABLED)

    def __init__(self, *, db_session_factory, neo4j_service):
        super().__init__()
        self.db_session_factory = db_session_factory
        self.neo4j_service = neo4j_service

    def supports(self, level: ContextLevel) -> bool:
        return True   # resource identity is the core of every context

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        # If the resolver already populated the full resource, use it directly.
        if resource.is_fully_resolved:
            data = {
                "resource_id":   resource.resource_id,
                "resource_name": resource.resource_name or resource.resource_id,
                "resource_type": resource.resource_type,
                "provider":      resource.provider or "aws",
                "region":        resource.region or "",
                "account_id":    resource.account_id or "",
                "arn":           resource.arn or "",
                "status":        resource.status or "unknown",
                "tags":          resource.tags or {},
            }
        else:
            # Resolver returned a stub – try the DB ourselves.
            data = self._fetch_from_db(resource.resource_id, resource.original_identifier)
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)

    # ------------------------------------------------------------------
    #  Private helpers
    # ------------------------------------------------------------------

    def _fetch_from_db(self, resource_id: str, original_identifier: str = "") -> Dict[str, Any]:
        try:
            from app.models import ResourceDB, ResourceNodeDB

            db = self.db_session_factory()
            try:
                # Try exact resource_id first
                row: Optional[ResourceDB] = (
                    db.query(ResourceDB)
                    .filter(ResourceDB.resource_id == resource_id)
                    .first()
                )
                # Fallback: search by name (catches user-supplied human names)
                if row is None and original_identifier:
                    row = (
                        db.query(ResourceDB)
                        .filter(ResourceDB.name.ilike(f"%{original_identifier}%"))
                        .first()
                    )

                if row:
                    tags: Dict = {}
                    if row.tags:
                        try:
                            tags = json.loads(row.tags)
                        except Exception:
                            pass
                    meta = row.resource_metadata or {}
                    arn = meta.get("arn", "") if isinstance(meta, dict) else ""
                    return {
                        "resource_id":       row.resource_id,
                        "resource_name":     row.name or row.resource_id,
                        "resource_type":     row.resource_type,
                        "provider": row.provider,
                        "region":   row.region or "",
                        "account_id":  str(row.cloud_account_id or ""),
                        "arn":      arn,
                        "status":   row.status or "unknown",
                        "tags":     tags,
                    }

                # Fallback: resource_nodes
                node: Optional[ResourceNodeDB] = (
                    db.query(ResourceNodeDB)
                    .filter(ResourceNodeDB.resource_id == resource_id)
                    .first()
                )
                if node:
                    return {
                        "resource_id":       node.resource_id,
                        "resource_name":     node.name or node.resource_id,
                        "resource_type":     node.resource_type,
                        "provider": node.provider,
                        "region":   "",
                        "account_id":  "",
                        "arn":      "",
                        "status":   "unknown",
                        "tags":     {},
                    }
            finally:
                db.close()

        except Exception as exc:
            logger.warning("ResourceProvider DB lookup failed for %s: %s", resource_id, exc)

        # Last resort: Neo4j MemoryGraphStore
        return self._fallback_from_neo4j(resource_id)

    def _fallback_from_neo4j(self, resource_id: str) -> Dict[str, Any]:
        try:
            node = self.neo4j_service.get_node(resource_id)
            if not node:
                raise ValueError("Node not found")
            return {
                "resource_id":       node.get("id", resource_id),
                "resource_name":     node.get("name", resource_id),
                "resource_type":     node.get("type", "unknown"),
                "provider": node.get("provider", "aws"),
                "region":   node.get("region", ""),
                "account_id":  "",
                "arn":      "",
                "status":   node.get("status", "unknown"),
                "tags":     {},
            }
        except Exception:
            return {
                "resource_id":       resource_id,
                "resource_name":     resource_id,
                "resource_type":     "unknown",
                "provider": "aws",
                "region":   "",
                "account_id":  "",
                "arn":      "",
                "status":   "unknown",
                "tags":     {},
            }
