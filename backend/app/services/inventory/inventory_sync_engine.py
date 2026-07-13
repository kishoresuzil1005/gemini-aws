"""
Inventory Sync Engine — Production Implementation
Synchronizes cloud discovery data into PostgreSQL incrementally using the InventoryDiffEngine.
"""
import logging
import time
from typing import Any, Dict, List, Optional

from app.providers.common.inventory_diff import InventoryDiffEngine

logger = logging.getLogger(__name__)


class InventorySyncEngine:
    """
    Coordinates incremental synchronization of cloud inventory to PostgreSQL.
    Uses InventoryDiffEngine to only insert/update/delete changed records.
    """

    def __init__(self, db_session=None):
        """
        Args:
            db_session: SQLAlchemy session or async session factory.
                        If None, runs in dry-run/log mode.
        """
        self.db = db_session
        self.inventory_diff = InventoryDiffEngine()

    def sync_to_postgres(
        self,
        provider: str,
        new_inventory: List[Dict[str, Any]],
        old_inventory: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Computes diff and applies incremental changes to the PostgreSQL inventory table.

        Args:
            provider: Cloud provider label.
            new_inventory: Fresh discovery results.
            old_inventory: Previously stored inventory. If None, treats all new as additions.

        Returns:
            Sync summary with counts.
        """
        start = time.perf_counter()
        old = old_inventory or []
        diff = self.inventory_diff.calculate_diff(old, new_inventory)

        counts = {
            "added": 0,
            "updated": 0,
            "removed": 0,
            "errors": 0,
        }

        if self.db:
            try:
                for resource in diff["added"]:
                    self._upsert_resource(resource, provider)
                    counts["added"] += 1

                for resource in diff["changed"]:
                    self._upsert_resource(resource, provider)
                    counts["updated"] += 1

                for resource in diff["removed"]:
                    self._delete_resource(resource.get("resource_id") or resource.get("id"), provider)
                    counts["removed"] += 1

            except Exception as e:
                logger.error(f"InventorySyncEngine failed for {provider}: {e}", exc_info=True)
                counts["errors"] += 1
        else:
            # Dry-run mode — just log what would happen
            counts["added"] = len(diff["added"])
            counts["updated"] = len(diff["changed"])
            counts["removed"] = len(diff["removed"])
            logger.info(
                f"[InventorySync/dry-run] {provider}: "
                f"+{counts['added']} ~{counts['updated']} -{counts['removed']}"
            )

        elapsed = round(time.perf_counter() - start, 3)
        summary = {
            "provider": provider,
            "status": "success" if counts["errors"] == 0 else "partial_error",
            "duration_seconds": elapsed,
            **counts,
        }
        logger.info(f"[InventorySync/{provider}] Done in {elapsed}s: {summary}")
        return summary

    def _upsert_resource(self, resource: Dict[str, Any], provider: str):
        """INSERT or UPDATE a resource in the inventory table."""
        if not self.db:
            return

        resource_id = resource.get("resource_id") or resource.get("id")
        resource_type = resource.get("resource_type") or resource.get("type") or "Resource"
        name = resource.get("name") or resource_id
        region = resource.get("region") or ""
        status = resource.get("status") or "unknown"
        metadata = resource.get("metadata") or {}

        # Use raw SQL for DB-agnostic operation without ORM model dependency
        from sqlalchemy import text
        import json

        sql = text("""
            INSERT INTO inventory (resource_id, resource_type, name, provider, region, status, metadata, updated_at)
            VALUES (:resource_id, :resource_type, :name, :provider, :region, :status, :metadata, NOW())
            ON CONFLICT (resource_id)
            DO UPDATE SET
                resource_type = EXCLUDED.resource_type,
                name = EXCLUDED.name,
                provider = EXCLUDED.provider,
                region = EXCLUDED.region,
                status = EXCLUDED.status,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
        """)

        self.db.execute(sql, {
            "resource_id": resource_id,
            "resource_type": resource_type,
            "name": name,
            "provider": provider,
            "region": region,
            "status": status,
            "metadata": json.dumps(metadata),
        })
        self.db.commit()

    def _delete_resource(self, resource_id: str, provider: str):
        """SOFT DELETE or ARCHIVE a removed resource."""
        if not self.db or not resource_id:
            return

        from sqlalchemy import text

        sql = text("""
            UPDATE inventory
            SET status = 'removed', updated_at = NOW()
            WHERE resource_id = :resource_id AND provider = :provider
        """)
        self.db.execute(sql, {"resource_id": resource_id, "provider": provider})
        self.db.commit()
        logger.debug(f"Soft-deleted resource: {resource_id} ({provider})")