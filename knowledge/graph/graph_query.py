# knowledge/graph/graph_query.py
"""API Boundary definitions for querying the Knowledge Graph."""

from typing import List, Optional
import abc

from .graph_models import GraphNode, GraphEdge

class GraphQueryAPI(abc.ABC):
    """Abstract interface defining the strict query contract for downstream AI and Analyzers."""

    @abc.abstractmethod
    def get_node(self, node_id: str) -> GraphNode:
        pass

    @abc.abstractmethod
    def get_edge(self, edge_id: str) -> GraphEdge:
        pass

    @abc.abstractmethod
    def find_nodes_by_type(self, node_type: str) -> List[GraphNode]:
        """e.g. 'RESOURCE' or 'RULE'"""
        pass

    @abc.abstractmethod
    def find_neighbors(self, node_id: str) -> List[GraphNode]:
        pass

    @abc.abstractmethod
    def find_dependencies(self, node_id: str) -> List[GraphNode]:
        pass

    @abc.abstractmethod
    def find_dependents(self, node_id: str) -> List[GraphNode]:
        pass

    @abc.abstractmethod
    def find_shortest_path(self, source_id: str, target_id: str) -> List[GraphEdge]:
        pass

    @abc.abstractmethod
    def search_graph(self, label: str) -> List[GraphNode]:
        pass
        
    @abc.abstractmethod
    def calculate_blast_radius(self, node_id: str) -> List[GraphNode]:
        pass
