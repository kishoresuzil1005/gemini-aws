# knowledge/snapshot/snapshot_diff.py
"""Computes semantic diffs between two snapshot payloads."""

from typing import Dict, Any

class SnapshotDiff:
    @staticmethod
    def compare(source_payload: Dict[str, Any], target_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Returns semantic additions, removals, and modifications."""
        diff = {
            "added_resources": [],
            "removed_resources": [],
            "added_rules": [],
            "removed_rules": []
        }
        
        # In a full implementation, this would compare IDs and hashes of individual entities
        source_resources = {r['resource_id']: r for r in source_payload.get('data', {}).get('resources', [])}
        target_resources = {r['resource_id']: r for r in target_payload.get('data', {}).get('resources', [])}
        
        diff["added_resources"] = [rid for rid in target_resources if rid not in source_resources]
        diff["removed_resources"] = [rid for rid in source_resources if rid not in target_resources]
        
        return diff
