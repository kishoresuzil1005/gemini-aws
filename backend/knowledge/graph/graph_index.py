# knowledge/graph/graph_index.py
"""In-memory indexing engine for the Unified Knowledge Graph."""

import logging
from typing import Dict, List, Set

from .graph_models import GraphNode, GraphEdge

logger = logging.getLogger(__name__)

class GraphIndex:
    """Maintains highly optimized Adjacency Lists and label indices for graph traversal."""

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        
        # Adjacency Lists: Mapping Node ID -> Set of Edge IDs
        self.outbound_edges: Dict[str, Set[str]] = {}
        self.inbound_edges: Dict[str, Set[str]] = {}
        
        # Label/Type Indices
        self.node_type_index: Dict[str, Set[str]] = {}
        self.edge_type_index: Dict[str, Set[str]] = {}
        self.label_index: Dict[str, Set[str]] = {}

    def build_indexes(self, nodes: List[GraphNode], edges: List[GraphEdge]) -> None:
        """Rebuilds the entire index from scratch."""
        self.clear()
        
        # Index Nodes
        for n in nodes:
            nid = n.node_id
            self.nodes[nid] = n
            self.node_type_index.setdefault(n.node_type, set()).add(nid)
            for label in n.labels:
                self.label_index.setdefault(label, set()).add(nid)
                
        # Index Edges
        for e in edges:
            eid = e.edge_id
            self.edges[eid] = e
            self.edge_type_index.setdefault(e.relationship_type, set()).add(eid)
            
            # Adjacency
            self.outbound_edges.setdefault(e.source_id, set()).add(eid)
            self.inbound_edges.setdefault(e.target_id, set()).add(eid)
            
        logger.info(f"Graph index rebuilt: {len(self.nodes)} nodes, {len(self.edges)} edges.")

    def clear(self) -> None:
        """Flush all indices."""
        self.nodes.clear()
        self.edges.clear()
        self.outbound_edges.clear()
        self.inbound_edges.clear()
        self.node_type_index.clear()
        self.edge_type_index.clear()
        self.label_index.clear()
