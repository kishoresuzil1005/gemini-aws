# knowledge/relationships/relationship_manager.py
"""Orchestrates relationship catalog lifecycle and state transitions."""

import logging
from typing import List

from .relationship_models import CanonicalRelationship
from .relationship_builder import RelationshipBuilder
from .relationship_index import RelationshipIndex
from .relationship_version_manager import RelationshipVersionManager
from ..catalog.catalog_models import CanonicalResource

logger = logging.getLogger(__name__)

class RelationshipManager:
    """Controls the rebuilding and indexing lifecycle."""

    def __init__(self, index: RelationshipIndex, version_manager: RelationshipVersionManager):
        self.index = index
        self.version_manager = version_manager
        self.builder = RelationshipBuilder()
        
        self.current_relationships: List[CanonicalRelationship] = []

    def update_relationships(self, resources: List[CanonicalResource]) -> None:
        """Extracts edges from a fresh resource catalog and rebuilds the relationship map."""
        
        # Build new relationships from the global resource set
        new_relationships = self.builder.build(resources)
        
        # Update State
        self.current_relationships = new_relationships
        self.version_manager.increment_version()
        
        # Rebuild Adjacency Indexes
        self.index.build_indexes(self.current_relationships)
        
        logger.info(f"Relationship Catalog updated. Total Edges: {len(self.current_relationships)}")
