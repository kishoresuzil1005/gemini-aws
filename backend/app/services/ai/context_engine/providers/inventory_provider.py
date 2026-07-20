"""InventoryProvider – fetches enriched inventory metadata from PostgreSQL.

Queries the ``resources`` table for account, environment, project,
owner, scanner version, and discovery metadata.  Expands beyond
basic resource identity with all CMDB-level fields.
"""

import json
import time
import logging
from typing import Any, Dict, Optional

from ..base_provider import BaseProvider
from ..common.constants import INVENTORY_PROVIDER_ENABLED, TTL_STATIC
from ..common.helpers import flag_enabled, iso_timestamp
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)


class InventoryProvider(BaseProvider):
    """Fetches enriched inventory metadata from the PostgreSQL asset store."""

    name       = "inventory"
    scope      = ProviderScope.STATIC
    priority   = 20
    output_key = "inventory"
    cache_ttl  = TTL_STATIC
    version    = "1.0"
    source     = "postgres"
    enabled    = flag_enabled(INVENTORY_PROVIDER_ENABLED)

    def __init__(self, *, db_session_factory):
        super().__init__()
        self.db_session_factory = db_session_factory

    def supports(self, level: ContextLevel) -> bool:
        return True

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        data = self._fetch_from_db(resource.resource_id)
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)

    # ------------------------------------------------------------------

    def _fetch_from_db(self, resource_id: str) -> Dict[str, Any]:
        try:
            from app.models import ResourceDB, CloudAccountDB

            db = self.db_session_factory()
            try:
                row: Optional[ResourceDB] = (
                    db.query(ResourceDB)
                    .filter(ResourceDB.resource_id == resource_id)
                    .first()
                )

                if not row:
                    return self._empty(resource_id)

                # Fetch account details
                account_id = ""
                organization = ""
                if row.cloud_account_id:
                    acct = db.query(CloudAccountDB).filter(
                        CloudAccountDB.id == row.cloud_account_id
                    ).first()
                    if acct:
                        account_id = acct.credentials_hint or ""
                        organization = acct.name or ""

                tags: Dict = {}
                if row.tags:
                    try:
                        tags = json.loads(row.tags)
                    except Exception:
                        pass

                meta = row.resource_metadata or {}
                environment = ""
                project = ""
                owner = ""
                if isinstance(meta, dict):
                    environment = meta.get("environment", tags.get("Environment", tags.get("env", "")))
                    project     = meta.get("project",     tags.get("Project",     tags.get("project", "")))
                    owner       = meta.get("owner",       tags.get("Owner",       tags.get("owner", "")))

                discovered_at_ts = row.discovered_at or 0
                from datetime import datetime, timezone
                discovered_iso = (
                    datetime.fromtimestamp(discovered_at_ts / 1000, tz=timezone.utc).isoformat()
                    if discovered_at_ts else iso_timestamp()
                )

                return {
                    "resource_id":     resource_id,
                    "account_id":      account_id,
                    "organization":    organization,
                    "environment":     environment or "",
                    "project":         project or "",
                    "region":          row.region or "",
                    "provider":        row.provider or "aws",
                    "owner":           owner or "",
                    "tags":            tags,
                    "metadata":        meta if isinstance(meta, dict) else {},
                    "scanner_version": "1.0.0",
                    "last_discovered": discovered_iso,
                }

            finally:
                db.close()

        except Exception as exc:
            logger.warning("InventoryProvider DB lookup failed for %s: %s", resource_id, exc)
            return self._empty(resource_id)

    def _empty(self, resource_id: str) -> Dict[str, Any]:
        return {
            "resource_id":     resource_id,
            "account_id":      "",
            "organization":    "",
            "environment":     "",
            "project":         "",
            "region":          "",
            "provider":        "aws",
            "owner":           "",
            "tags":            {},
            "metadata":        {},
            "scanner_version": "1.0.0",
            "last_discovered": iso_timestamp(),
        }
