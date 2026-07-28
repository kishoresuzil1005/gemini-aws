# knowledge/graph/graph_analytics.py
"""Advanced analytics running on top of the Graph Engine."""

from typing import List, Set
from collections import deque

from .graph_index import GraphIndex
from .graph_models import GraphNode
from .graph_traversal import GraphTraversal

class GraphAnalytics:
    """Executes high-order topology evaluations."""

    def __init__(self, index: GraphIndex, traversal: GraphTraversal):
        self.index = index
        self.traversal = traversal

    def calculate_blast_radius(self, root_node_id: str) -> List[GraphNode]:
        """
        Determines how many systems fail if the root node goes offline.
        Traverses outbound strictly along DEPENDS_ON and connected topological edges.
        """
        if root_node_id not in self.index.nodes:
            return []
            
        visited_ids: Set[str] = {root_node_id}
        queue = deque([root_node_id])
        
        while queue:
            current = queue.popleft()
            
            # Find what depends on 'current' (backward_edges where edge type is DEPENDS_ON)
            # Actually, if A depends on B, the edge is A -> B. 
            # If B fails, A fails. So we want inbound edges to B where type == DEPENDS_ON.
            
            inbound_eids = self.index.inbound_edges.get(current, set())
            for eid in inbound_eids:
                edge = self.index.edges.get(eid)
                if not edge:
                    continue
                    
                if edge.relationship_type in ("DEPENDS_ON", "CONNECTED_TO", "ROUTES_TO"):
                    dependent_id = edge.source_id
                    if dependent_id not in visited_ids:
                        visited_ids.add(dependent_id)
                        queue.append(dependent_id)
                        
        # Resolve IDs back to nodes
        return [self.index.nodes[nid] for nid in visited_ids]

    def analyze_security_exposure(self, node_id: str) -> List[GraphNode]:
        """Maps effective privilege escalation via ASSUMES_ROLE and GRANTS_PERMISSION."""
        # Simplified equivalent of blast radius but constrained to security edges.
        if node_id not in self.index.nodes:
            return []
            
        visited_ids: Set[str] = {node_id}
        queue = deque([node_id])
        
        while queue:
            current = queue.popleft()
            outbound_eids = self.index.outbound_edges.get(current, set())
            for eid in outbound_eids:
                edge = self.index.edges.get(eid)
                if edge and edge.relationship_type in ("ASSUMES_ROLE", "GRANTS_PERMISSION", "TRUSTS"):
                    target_id = edge.target_id
                    if target_id not in visited_ids:
                        visited_ids.add(target_id)
                        queue.append(target_id)
                        
        return [self.index.nodes[nid] for nid in visited_ids]
