# knowledge/graph/graph_importer.py
"""Deserializes the Knowledge Graph from JSON snapshots."""

import json
import logging
from typing import Tuple, List

from .graph_models import GraphNode, GraphEdge

logger = logging.getLogger(__name__)

class GraphImporter:
    """Loads snapshot data from disk back into memory."""

    def import_snapshot(self, filepath: str) -> Tuple[List[GraphNode], List[GraphEdge]]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            nodes = [GraphNode(**n) for n in data.get("nodes", [])]
            edges = [GraphEdge(**e) for e in data.get("edges", [])]
            return nodes, edges
        except Exception as exc:
            logger.error(f"Failed to import graph snapshot: {exc}")
            return [], []
