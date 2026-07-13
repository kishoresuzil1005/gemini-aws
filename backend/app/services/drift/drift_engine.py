"""
Drift Engine — Production Implementation
Detects infrastructure drift by comparing stored inventory against live AWS state.
"""
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DriftEngine:
    """
    Compares stored inventory snapshots to live cloud discovery results.
    Produces a structured drift report with per-resource change details.
    """

    def __init__(self):
        self._last_scan_time: Optional[float] = None

    def detect_drift(
        self,
        stored_inventory: List[Dict[str, Any]],
        live_inventory: List[Dict[str, Any]],
        provider: str = "aws",
    ) -> Dict[str, Any]:
        """
        Core drift detection algorithm.

        Args:
            stored_inventory: Previously persisted inventory (from PostgreSQL / last sync).
            live_inventory: Current live state from cloud provider SDK.
            provider: Cloud provider label for attribution.

        Returns:
            Drift report with added, removed, changed, and unchanged counts.
        """
        self._last_scan_time = time.time()

        stored_map = {r.get("resource_id") or r.get("id"): r for r in stored_inventory if r.get("resource_id") or r.get("id")}
        live_map = {r.get("resource_id") or r.get("id"): r for r in live_inventory if r.get("resource_id") or r.get("id")}

        added: List[Dict] = []
        removed: List[Dict] = []
        changed: List[Dict] = []
        unchanged: int = 0

        # Detect added and changed resources
        for resource_id, live_resource in live_map.items():
            if resource_id not in stored_map:
                added.append({
                    "resource_id": resource_id,
                    "resource_type": live_resource.get("resource_type", "unknown"),
                    "name": live_resource.get("name", resource_id),
                    "region": live_resource.get("region", ""),
                    "drift_type": "added",
                    "live_state": live_resource,
                    "stored_state": None,
                })
            else:
                stored_resource = stored_map[resource_id]
                field_changes = self._compare_fields(stored_resource, live_resource)
                if field_changes:
                    changed.append({
                        "resource_id": resource_id,
                        "resource_type": live_resource.get("resource_type", "unknown"),
                        "name": live_resource.get("name", resource_id),
                        "region": live_resource.get("region", ""),
                        "drift_type": "changed",
                        "field_changes": field_changes,
                        "live_state": live_resource,
                        "stored_state": stored_resource,
                    })
                else:
                    unchanged += 1

        # Detect removed resources
        for resource_id in stored_map:
            if resource_id not in live_map:
                stored_resource = stored_map[resource_id]
                removed.append({
                    "resource_id": resource_id,
                    "resource_type": stored_resource.get("resource_type", "unknown"),
                    "name": stored_resource.get("name", resource_id),
                    "region": stored_resource.get("region", ""),
                    "drift_type": "removed",
                    "live_state": None,
                    "stored_state": stored_resource,
                })

        drift_detected = bool(added or removed or changed)
        logger.info(
            f"[DriftEngine/{provider}] Drift scan complete: "
            f"+{len(added)} added, -{len(removed)} removed, ~{len(changed)} changed, "
            f"{unchanged} unchanged. Drift detected: {drift_detected}"
        )

        return {
            "provider": provider,
            "scan_time": self._last_scan_time,
            "drift_detected": drift_detected,
            "summary": {
                "added": len(added),
                "removed": len(removed),
                "changed": len(changed),
                "unchanged": unchanged,
                "total_live": len(live_map),
                "total_stored": len(stored_map),
            },
            "added": added,
            "removed": removed,
            "changed": changed,
        }

    def _compare_fields(
        self,
        stored: Dict[str, Any],
        live: Dict[str, Any],
        tracked_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Compares key fields between stored and live resources.
        Returns a list of changed fields with before/after values.
        """
        if tracked_fields is None:
            tracked_fields = ["status", "name", "region", "metadata"]

        changes = []
        for field in tracked_fields:
            stored_val = stored.get(field)
            live_val = live.get(field)
            if stored_val != live_val:
                changes.append({
                    "field": field,
                    "before": stored_val,
                    "after": live_val,
                })
        return changes