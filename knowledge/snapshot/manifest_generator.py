# knowledge/snapshot/manifest_generator.py
"""Generates the Bill of Materials for a snapshot."""

from typing import Dict, Any
from .snapshot_models import SnapshotManifest

class ManifestGenerator:
    @staticmethod
    def generate(snapshot_id: str, version: str, checksum: str, stats: Dict[str, int]) -> SnapshotManifest:
        return SnapshotManifest(
            snapshot_id=snapshot_id,
            version=version,
            checksum=checksum,
            resource_count=stats.get("resource_count", 0),
            relationship_count=stats.get("relationship_count", 0),
            rule_count=stats.get("rule_count", 0)
        )
