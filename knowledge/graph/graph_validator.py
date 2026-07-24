# knowledge/graph/graph_validator.py
"""Ensures graph integrity (no dangling edges)."""

import logging
from typing import List

from .graph_models import GraphNode, GraphEdge
from .graph_exceptions import DisconnectedGraphError

logger = logging.getLogger(__name__)

class GraphValidator:
    """Runs connectivity and schema checks before finalizing graph build."""

    def validate(self, nodes: List[GraphNode], edges: List[GraphEdge]) -> List[GraphEdge]:
        """Strip edges that reference non-existent nodes."""
        valid_node_ids = {n.node_id for n in nodes}
        valid_edges = []
        dangling_count = 0
        
        for e in edges:
            if e.source_id in valid_node_ids and e.target_id in valid_node_ids:
                valid_edges.append(e)
            else:
                dangling_count += 1
                
        if dangling_count > 0:
            logger.warning(f"Graph validator stripped {dangling_count} dangling edges.")
            
        return valid_edges
