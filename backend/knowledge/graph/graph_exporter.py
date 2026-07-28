# knowledge/graph/graph_exporter.py
"""Serializes the Knowledge Graph to JSON for snapshots."""

import json
import logging
from typing import List

from .graph_models import GraphNode, GraphEdge

logger = logging.getLogger(__name__)

class GraphExporter:
    """Exports in-memory nodes and edges to disk."""

    def export_snapshot(self, filepath: str, nodes: List[GraphNode], edges: List[GraphEdge]) -> None:
        try:
            payload = {
                "nodes": [n.dict() for n in nodes],
                "edges": [e.dict() for e in edges]
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            logger.info(f"Graph snapshot exported to {filepath}")
        except Exception as exc:
            logger.error(f"Failed to export graph snapshot: {exc}")
