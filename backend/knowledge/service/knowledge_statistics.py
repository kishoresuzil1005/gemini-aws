# knowledge/service/knowledge_statistics.py
"""Aggregates metrics from across the Knowledge Platform."""

from typing import Dict, Any

class KnowledgeStatistics:
    def __init__(self, resource_cat, rel_cat, rule_cat, graph):
        self.resource_cat = resource_cat
        self.rel_cat = rel_cat
        self.rule_cat = rule_cat
        self.graph = graph

    def get_stats(self) -> Dict[str, Any]:
        """Gathers basic size metrics."""
        return {
            "total_resources": len(self.resource_cat.list_resources()),
            "total_rules": len(self.rule_cat.list_rules()),
            "total_nodes": len(self.graph.index.nodes),
            "total_edges": len(self.graph.index.edges)
        }
