# knowledge/graph/graph_snapshot_manager.py
"""Orchestrates saving and loading point-in-time graph states."""

from typing import List, Tuple

from .graph_models import GraphNode, GraphEdge
from .graph_exporter import GraphExporter
from .graph_importer import GraphImporter
from .graph_version_manager import GraphVersionManager

class GraphSnapshotManager:
    """Facade for I/O and version control of the graph."""

    def __init__(self, version_manager: GraphVersionManager):
        self.version_manager = version_manager
        self.exporter = GraphExporter()
        self.importer = GraphImporter()

    def create_snapshot(self, filepath: str, nodes: List[GraphNode], edges: List[GraphEdge]) -> str:
        """Exports the graph and bumps the semantic version."""
        self.exporter.export_snapshot(filepath, nodes, edges)
        return self.version_manager.increment_version()
        
    def load_snapshot(self, filepath: str) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Imports the graph from disk."""
        return self.importer.import_snapshot(filepath)
