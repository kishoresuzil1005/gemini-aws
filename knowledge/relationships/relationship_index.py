# knowledge/relationships/relationship_index.py
"""High-performance Adjacency List for O(1) multi-hop querying."""

import logging
from typing import Dict, List, Set

from .relationship_models import CanonicalRelationship

logger = logging.getLogger(__name__)

class RelationshipIndex:
    """Maintains highly optimized adjacency lists for graph traversal without a database."""

    def __init__(self):
        # Fast full lookup
        self.id_index: Dict[str, CanonicalRelationship] = {}
        
        # Adjacency Lists
        # Mapping Node ID -> Set of outgoing Relationship IDs
        self.forward_edges: Dict[str, Set[str]] = {}
        
        # Mapping Node ID -> Set of incoming Relationship IDs
        self.backward_edges: Dict[str, Set[str]] = {}
        
        # Type-based filtering
        self.type_index: Dict[str, Set[str]] = {}

    def build_indexes(self, relationships: List[CanonicalRelationship]) -> None:
        """Rebuilds the adjacency list from scratch."""
        self.clear()
        
        for rel in relationships:
            rid = rel.relationship_id
            src = rel.source_resource_id
            tgt = rel.target_resource_id
            
            self.id_index[rid] = rel
            
            # Populate Adjacency List
            self.forward_edges.setdefault(src, set()).add(rid)
            self.backward_edges.setdefault(tgt, set()).add(rid)
            
            # Type Index
            self.type_index.setdefault(rel.relationship_type, set()).add(rid)
            
        logger.info("Relationship index rebuilt successfully.")

    def clear(self) -> None:
        """Flushes the adjacency lists."""
        self.id_index.clear()
        self.forward_edges.clear()
        self.backward_edges.clear()
        self.type_index.clear()
