# knowledge/graph/knowledge_graph.py
"""Unified facade exposing the complete Enterprise Knowledge Graph functionality."""

from typing import List

from .graph_models import GraphNode, GraphEdge
from .graph_index import GraphIndex
from .graph_query import GraphQueryAPI
from .graph_traversal import GraphTraversal
from .graph_analytics import GraphAnalytics
from .graph_manager import GraphManager
from .graph_version_manager import GraphVersionManager
from .graph_snapshot_manager import GraphSnapshotManager
from .graph_exceptions import NodeNotFoundError, EdgeNotFoundError

from ..catalog.catalog_models import CanonicalResource
from ..relationships.relationship_models import CanonicalRelationship
from ..rules.rule_models import CanonicalRule

class KnowledgeGraph(GraphQueryAPI):
    """The absolute Single Source of Truth for the Knowledge Platform.
    
    Synthesizes Resources, Relationships, and Rules into a unified, high-performance
    in-memory directed graph. Downstream Analyzers execute topological queries against this.
    """

    def __init__(self):
        self.index = GraphIndex()
        self.version_manager = GraphVersionManager()
        self.snapshot_manager = GraphSnapshotManager(self.version_manager)
        self.manager = GraphManager(self.index, self.snapshot_manager)
        
        self.traversal = GraphTraversal(self.index)
        self.analytics = GraphAnalytics(self.index, self.traversal)

    # Lifecycle Methods
    
    def ingest(self, resources: List[CanonicalResource], relationships: List[CanonicalRelationship], rules: List[CanonicalRule]) -> None:
        """Fully rebuilds the graph from the underlying catalogs."""
        self.manager.update_graph(resources, relationships, rules)

    def load_snapshot(self, filepath: str) -> None:
        """Load and index a graph snapshot from disk."""
        nodes, edges = self.snapshot_manager.load_snapshot(filepath)
        if nodes and edges:
            self.manager.apply_snapshot(nodes, edges)

    def save_snapshot(self, filepath: str) -> str:
        """Persist the current graph state to disk and return the new version string."""
        return self.snapshot_manager.create_snapshot(filepath, self.manager.current_nodes, self.manager.current_edges)

    # Query API Implementation

    def get_node(self, node_id: str) -> GraphNode:
        node = self.index.nodes.get(node_id)
        if not node:
            raise NodeNotFoundError(f"Node {node_id} not found.")
        return node

    def get_edge(self, edge_id: str) -> GraphEdge:
        edge = self.index.edges.get(edge_id)
        if not edge:
            raise EdgeNotFoundError(f"Edge {edge_id} not found.")
        return edge

    def find_nodes_by_type(self, node_type: str) -> List[GraphNode]:
        ids = self.index.node_type_index.get(node_type.upper(), set())
        return [self.index.nodes[nid] for nid in ids]

    def find_neighbors(self, node_id: str) -> List[GraphNode]:
        return self.traversal.get_neighbors(node_id, direction="BOTH")

    def find_dependencies(self, node_id: str) -> List[GraphNode]:
        return self.traversal.get_neighbors(node_id, direction="OUTBOUND")

    def find_dependents(self, node_id: str) -> List[GraphNode]:
        return self.traversal.get_neighbors(node_id, direction="INBOUND")

    def find_shortest_path(self, source_id: str, target_id: str) -> List[GraphEdge]:
        return self.traversal.shortest_path(source_id, target_id)

    def search_graph(self, label: str) -> List[GraphNode]:
        ids = self.index.label_index.get(label, set())
        return [self.index.nodes[nid] for nid in ids]

    def calculate_blast_radius(self, node_id: str) -> List[GraphNode]:
        return self.analytics.calculate_blast_radius(node_id)
        
    def analyze_security_exposure(self, node_id: str) -> List[GraphNode]:
        return self.analytics.analyze_security_exposure(node_id)
