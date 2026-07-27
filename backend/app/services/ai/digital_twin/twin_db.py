"""Digital Twin Database — Phase 5"""
from __future__ import annotations
import json, time
from typing import Any, Dict, List, Optional
from app.services.ai.orchestrator.cache import OrchestratorCache


class DigitalTwinDB:
    """
    Stores versioned snapshots of infrastructure resources.
    Backed by Redis with optional Postgres persistence hook.
    """

    def __init__(self):
        self._cache = OrchestratorCache(ttl=86400)  # 24h

    def snapshot(self, resource_id: str, data: Dict[str, Any], version: Optional[str] = None) -> str:
        """Store a new snapshot. Returns the version key."""
        ver = version or str(int(time.time()))
        key = f"twin:{resource_id}:{ver}"
        self._cache.set(key, {"resource_id": resource_id, "version": ver, "data": data, "ts": time.time()})
        # Update version index
        idx_key = f"twin_versions:{resource_id}"
        existing = self._cache.get(idx_key) or []
        existing.append(ver)
        self._cache.set(idx_key, existing)
        return ver

    def get(self, resource_id: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a specific version or the latest snapshot."""
        if not version:
            idx = self._cache.get(f"twin_versions:{resource_id}") or []
            if not idx:
                return None
            version = idx[-1]
        return self._cache.get(f"twin:{resource_id}:{version}")

    def history(self, resource_id: str) -> List[str]:
        return self._cache.get(f"twin_versions:{resource_id}") or []
