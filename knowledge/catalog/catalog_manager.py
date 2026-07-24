# knowledge/catalog/catalog_manager.py
"""Orchestrates catalog lifecycle and state transitions."""

import logging
from typing import List

from .catalog_models import CanonicalResource
from .catalog_builder import CatalogBuilder
from .catalog_index import CatalogIndex
from .catalog_version_manager import CatalogVersionManager
from .catalog_metadata import CatalogMetadata

logger = logging.getLogger(__name__)

class CatalogManager:
    """Controls the rebuilding and indexing lifecycle."""

    def __init__(self, index: CatalogIndex, version_manager: CatalogVersionManager):
        self.index = index
        self.version_manager = version_manager
        self.builder = CatalogBuilder()
        
        self.current_resources: List[CanonicalResource] = []
        self.metadata: CatalogMetadata = CatalogMetadata()

    def update_catalog(self, new_candidates: List[CanonicalResource]) -> CatalogMetadata:
        """Merges new data, bumps version, and rebuilds indexes."""
        # Merge existing with new
        combined = self.current_resources + new_candidates
        
        # Build and deduplicate
        final_list, meta = self.builder.build(combined)
        
        # Update State
        self.current_resources = final_list
        meta.catalog_version = self.version_manager.increment_version()
        self.metadata = meta
        
        # Rebuild Indexes
        self.index.build_indexes(self.current_resources)
        
        logger.info(f"Catalog updated to version {self.metadata.catalog_version}")
        return self.metadata
