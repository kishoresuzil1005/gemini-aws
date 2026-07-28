# knowledge/graph/graph_manager.py
"""Orchestrates graph lifecycle, memory optimization, and state transitions."""

import logging
from typing import List

from .graph_models import GraphNode, GraphEdge
from .graph_builder import GraphBuilder
from .graph_index import GraphIndex
from .graph_optimizer import GraphOptimizer
from .graph_snapshot_manager import GraphSnapshotManager
from ..catalog.catalog_models import CanonicalResource
from ..relationships.relationship_models import CanonicalRelationship
from ..rules.rule_models import CanonicalRule

logger = logging.getLogger(__name__)

class GraphManager:
    """Controls the rebuilding, optimization, and indexing lifecycle of the Graph."""

    def __init__(self, index: GraphIndex, snapshot_manager: GraphSnapshotManager):
        self.index = index
        self.snapshot_manager = snapshot_manager
        self.builder = GraphBuilder()
        self.optimizer = GraphOptimizer()
        
        self.current_nodes: List[GraphNode] = []
        self.current_edges: List[GraphEdge] = []

    def update_graph(self, resources: List[CanonicalResource], relationships: List[CanonicalRelationship], rules: List[CanonicalRule]) -> None:
        """Synthesizes raw catalog data into the unified graph."""
        
        # Build
        nodes, edges = self.builder.build(resources, relationships, rules)
        
        # Optimize
        self.optimizer.optimize()
        
        # Update State
        self.current_nodes = nodes
        self.current_edges = edges
        
        # Rebuild Indexes
        self.index.build_indexes(self.current_nodes, self.current_edges)
        
        logger.info(f"Knowledge Graph updated.")

    def apply_snapshot(self, nodes: List[GraphNode], edges: List[GraphEdge]) -> None:
        """Directly applies loaded snapshot data to the active state."""
        self.current_nodes = nodes
        self.current_edges = edges
        self.index.build_indexes(self.current_nodes, self.current_edges)
        logger.info(f"Graph snapshot applied.")
