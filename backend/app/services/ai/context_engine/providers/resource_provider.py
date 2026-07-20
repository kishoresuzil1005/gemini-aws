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

    def supports(self, level: ContextLevel) -> bool:
        return True   # runs at every context level

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        data = self._fetch_from_db(resource.resource_id)
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)

    # ------------------------------------------------------------------
    #  Private helpers
    # ------------------------------------------------------------------

    def _fetch_from_db(self, resource_id: str) -> Dict[str, Any]:
        """Query PostgreSQL for the resource record."""
        try:
            from app.database import SessionLocal
            from app.models import ResourceDB, ResourceNodeDB

            db = SessionLocal()
            try:
                row: Optional[ResourceDB] = (
                    db.query(ResourceDB)
                    .filter(ResourceDB.resource_id == resource_id)
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
                        "id":       row.resource_id,
                        "name":     row.name or row.resource_id,
                        "type":     row.resource_type,
                        "provider": row.provider,
                        "region":   row.region or "",
                        "account":  str(row.cloud_account_id or ""),
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
                        "id":       node.resource_id,
                        "name":     node.name or node.resource_id,
                        "type":     node.resource_type,
                        "provider": node.provider,
                        "region":   "",
                        "account":  "",
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
            from app.services.graph.neo4j_service import MemoryGraphStore
            node = MemoryGraphStore.nodes.get(resource_id, {})
            return {
                "id":       node.get("id", resource_id),
                "name":     node.get("name", resource_id),
                "type":     node.get("type", "unknown"),
                "provider": node.get("provider", "aws"),
                "region":   node.get("region", ""),
                "account":  "",
                "arn":      "",
                "status":   node.get("status", "unknown"),
                "tags":     {},
            }
        except Exception:
            return {
                "id":       resource_id,
                "name":     resource_id,
                "type":     "unknown",
                "provider": "aws",
                "region":   "",
                "account":  "",
                "arn":      "",
                "status":   "unknown",
                "tags":     {},
            }
