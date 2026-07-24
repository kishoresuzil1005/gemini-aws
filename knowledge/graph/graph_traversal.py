# knowledge/graph/graph_traversal.py
"""Core graph traversal algorithms (BFS, DFS, shortest path)."""

from collections import deque
from typing import List, Set, Dict

from .graph_index import GraphIndex
from .graph_models import GraphNode, GraphEdge

class GraphTraversal:
    """Provides pure-Python traversal mechanics over the GraphIndex."""
    
    def __init__(self, index: GraphIndex):
        self.index = index

    def shortest_path(self, source_id: str, target_id: str) -> List[GraphEdge]:
        """Executes unweighted BFS to find shortest path between two nodes."""
        if source_id == target_id:
            return []
            
        queue = deque([(source_id, [])])
        visited: Set[str] = {source_id}
        
        while queue:
            current, path = queue.popleft()
            
            outbound_edge_ids = self.index.outbound_edges.get(current, set())
            
            for eid in outbound_edge_ids:
                edge = self.index.edges.get(eid)
                if not edge:
                    continue
                    
                next_node = edge.target_id
                
                if next_node == target_id:
                    return path + [edge]
                    
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [edge]))
                    
        return []
        
    def get_neighbors(self, node_id: str, direction: str = "BOTH") -> List[GraphNode]:
        """Returns neighboring nodes based on edge direction."""
        eids = set()
        if direction in ("OUTBOUND", "BOTH"):
            eids.update(self.index.outbound_edges.get(node_id, set()))
        if direction in ("INBOUND", "BOTH"):
            eids.update(self.index.inbound_edges.get(node_id, set()))
            
        neighbors = []
        for eid in eids:
            edge = self.index.edges.get(eid)
            if not edge:
                continue
            
            # Identify the node on the other side of the edge
            tgt_id = edge.target_id if edge.source_id == node_id else edge.source_id
            if tgt_id in self.index.nodes:
                neighbors.append(self.index.nodes[tgt_id])
                
        return neighbors
