# knowledge/snapshot/snapshot_statistics.py
"""Computes statistics for a snapshot payload."""

from typing import Dict, Any

class SnapshotStatistics:
    @staticmethod
    def compute(payload: Dict[str, Any]) -> Dict[str, int]:
        return {
            "resource_count": len(payload.get("resources", [])),
            "relationship_count": len(payload.get("relationships", [])),
            "rule_count": len(payload.get("rules", [])),
            "graph_node_count": len(payload.get("graph_nodes", [])),
            "graph_edge_count": len(payload.get("graph_edges", []))
        }
