# knowledge/relationships/relationship_catalog.py
"""Unified facade exposing the complete Relationship Catalog functionality."""

from typing import List, Set
from collections import deque

from .relationship_models import CanonicalRelationship
from .relationship_index import RelationshipIndex
from .relationship_query import RelationshipQueryAPI
from .relationship_manager import RelationshipManager
from .relationship_version_manager import RelationshipVersionManager
from .relationship_exceptions import RelationshipNotFoundError
from ..catalog.catalog_models import CanonicalResource

class RelationshipCatalog(RelationshipQueryAPI):
    """The central authoritative registry for Canonical Relationships.
    
    Implements the RelationshipQueryAPI to serve as the unified API boundary for
    graph traversals, dependency analysis, and network pathing.
    """

    def __init__(self):
        self.index = RelationshipIndex()
        self.version_manager = RelationshipVersionManager()
        self.manager = RelationshipManager(self.index, self.version_manager)

    # Lifecycle
    
    def ingest_from_resources(self, resources: List[CanonicalResource]) -> None:
        """Derives and indexes relationships based on the Resource Catalog."""
        self.manager.update_relationships(resources)

    # Internal Helpers
    
    def _resolve_ids(self, ids: set) -> List[CanonicalRelationship]:
        return [self.index.id_index[rid] for rid in ids if rid in self.index.id_index]

    # Query API Implementation

    def get_relationship(self, relationship_id: str) -> CanonicalRelationship:
        rel = self.index.id_index.get(relationship_id)
        if not rel:
            raise RelationshipNotFoundError(f"Relationship {relationship_id} not found.")
        return rel

    def find_relationships(self, resource_id: str) -> List[CanonicalRelationship]:
        """Returns all inbound and outbound relationships for a node."""
        outbound = self.index.forward_edges.get(resource_id, set())
        inbound = self.index.backward_edges.get(resource_id, set())
        return self._resolve_ids(outbound | inbound)

    def find_dependencies(self, resource_id: str) -> List[CanonicalRelationship]:
        """Returns outbound relationships (what this node depends on)."""
        return self._resolve_ids(self.index.forward_edges.get(resource_id, set()))

    def find_dependents(self, resource_id: str) -> List[CanonicalRelationship]:
        """Returns inbound relationships (what depends on this node)."""
        return self._resolve_ids(self.index.backward_edges.get(resource_id, set()))

    def find_network_path(self, source_id: str, target_id: str) -> List[CanonicalRelationship]:
        """Executes a multi-hop BFS pathfinding query between two nodes.
        
        Returns a list of relationships forming the shortest path, or an empty list.
        """
        if source_id == target_id:
            return []
            
        # BFS Queue stores tuples of (current_node, path_of_relationship_ids)
        queue = deque([(source_id, [])])
        visited: Set[str] = {source_id}
        
        while queue:
            current, path = queue.popleft()
            
            # Get all outgoing edges from the current node
            outgoing_rel_ids = self.index.forward_edges.get(current, set())
            
            for rel_id in outgoing_rel_ids:
                rel = self.index.id_index.get(rel_id)
                if not rel:
                    continue
                    
                next_node = rel.target_resource_id
                
                if next_node == target_id:
                    return self._resolve_ids(set(path + [rel_id]))
                    
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [rel_id]))
                    
        return []

    def find_security_relationships(self, resource_id: str) -> List[CanonicalRelationship]:
        """Filters relationships for security specific edges (e.g. ASSUMES_ROLE)."""
        all_rels = self.find_relationships(resource_id)
        sec_types = {"ASSUMES_ROLE", "GRANTS_PERMISSION", "TRUSTS", "AUTHORIZES"}
        return [r for r in all_rels if r.relationship_type in sec_types]
