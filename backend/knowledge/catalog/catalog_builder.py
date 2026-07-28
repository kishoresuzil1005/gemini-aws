# knowledge/catalog/catalog_builder.py
"""Builds and compiles the catalog from M7 normalized output."""

import logging
from typing import List, Dict

from .catalog_models import CanonicalResource
from .catalog_validator import CatalogValidator
from .catalog_metadata import CatalogMetadata

logger = logging.getLogger(__name__)

class CatalogBuilder:
    """Ingests Canonical Models and compiles them into a deduplicated list."""

    def __init__(self):
        self.validator = CatalogValidator()

    def build(self, resources: List[CanonicalResource]) -> tuple[List[CanonicalResource], CatalogMetadata]:
        """Validates and deduplicates incoming resources to form the fresh catalog state."""
        logger.info(f"Building catalog from {len(resources)} raw canonical models.")
        
        # 1. Validation
        valid_resources = self.validator.validate(resources)
        
        # 2. Final Catalog-level Deduplication
        # (Even though M7 deduplicates per-snapshot, the Builder deduplicates across the entire corpus)
        merged: Dict[str, CanonicalResource] = {}
        for res in valid_resources:
            rid = res.resource_id
            if rid in merged:
                # Naive merge strategy for demonstration: newest properties win
                existing = merged[rid]
                existing.properties.update(res.properties)
                existing.tags.update(res.tags)
                existing.aliases.extend(res.aliases)
            else:
                merged[rid] = res
                
        final_list = list(merged.values())
        
        # 3. Metadata generation
        providers = set(r.provider for r in final_list)
        services = set(r.service for r in final_list)
        
        meta = CatalogMetadata(
            total_resources=len(final_list),
            total_providers=len(providers),
            total_services=len(services)
        )
        
        logger.info(f"Catalog build complete. Final size: {meta.total_resources} resources.")
        return final_list, meta
