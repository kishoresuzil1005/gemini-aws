# knowledge/snapshot/snapshot_builder.py
"""Aggregates the total state of the Knowledge Platform."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SnapshotBuilder:
    def __init__(self, resource_cat, rel_cat, rule_cat, graph):
        self.resource_cat = resource_cat
        self.rel_cat = rel_cat
        self.rule_cat = rule_cat
        self.graph = graph

    def build_payload(self) -> Dict[str, Any]:
        """Pulls the entire memory state into a single dictionary."""
        
        # Note: In a real system, we'd use iterators or direct object dumps.
        # This assumes the catalogs have methods exposing their dict representations.
        logger.info("Building comprehensive snapshot payload...")
        
        return {
            "resources": [r.dict() for r in self.resource_cat.list_resources()],
            "relationships": [r.dict() for r in self.rel_cat.list_relationships()],
            "rules": [r.dict() for r in self.rule_cat.list_rules()],
            "graph_nodes": [n.dict() for n in self.graph.index.nodes.values()],
            "graph_edges": [e.dict() for e in self.graph.index.edges.values()]
        }
