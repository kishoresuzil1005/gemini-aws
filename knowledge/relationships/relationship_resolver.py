# knowledge/relationships/relationship_resolver.py
"""Resolves aliases or dangling references in the relationship map."""

import logging
from typing import List

from .relationship_models import CanonicalRelationship

logger = logging.getLogger(__name__)

class RelationshipResolver:
    """Handles logic for pointing aliases to canonical IDs or stripping dead edges."""

    def resolve(self, relationships: List[CanonicalRelationship], valid_node_ids: set) -> List[CanonicalRelationship]:
        """Strip edges where either the source or target node is missing from the global catalog."""
        resolved = []
        dangling_count = 0
        
        # If valid_node_ids is empty, we assume we are not verifying against a global catalog yet.
        if not valid_node_ids:
            return relationships
            
        for rel in relationships:
            if rel.source_resource_id in valid_node_ids and rel.target_resource_id in valid_node_ids:
                resolved.append(rel)
            else:
                dangling_count += 1
                
        if dangling_count > 0:
            logger.warning(f"Dropped {dangling_count} dangling relationships during resolution.")
            
        return resolved
