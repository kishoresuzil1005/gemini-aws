# knowledge/catalog/catalog_index.py
"""In-memory indexing engine for O(1) lookups."""

import logging
from typing import Dict, List, Set

from .catalog_models import CanonicalResource

logger = logging.getLogger(__name__)

class CatalogIndex:
    """Maintains highly optimized reverse-indexes for rapid querying."""

    def __init__(self):
        # Primary lookup
        self.id_index: Dict[str, CanonicalResource] = {}
        
        # Categorical indexes (Storing Resource IDs to save memory)
        self.provider_index: Dict[str, Set[str]] = {}
        self.service_index: Dict[str, Set[str]] = {}
        self.category_index: Dict[str, Set[str]] = {}
        self.tag_index: Dict[str, Set[str]] = {}
        self.alias_index: Dict[str, str] = {} # Alias -> Resource ID

    def build_indexes(self, resources: List[CanonicalResource]) -> None:
        """Rebuilds all indexes from a fresh list of resources."""
        self.clear()
        
        for res in resources:
            rid = res.resource_id
            self.id_index[rid] = res
            
            # Provider
            prov = res.provider.lower()
            self.provider_index.setdefault(prov, set()).add(rid)
            
            # Service
            srv = res.service.lower()
            self.service_index.setdefault(srv, set()).add(rid)
            
            # Category
            cat = res.category.lower()
            self.category_index.setdefault(cat, set()).add(rid)
            
            # Tags
            for tk, tv in res.tags.items():
                tag_key = f"{tk}:{tv}".lower()
                self.tag_index.setdefault(tag_key, set()).add(rid)
                
            # Aliases
            for alias in res.aliases:
                self.alias_index[alias.lower()] = rid
                
        logger.info("Catalog indexes built successfully.")

    def clear(self) -> None:
        """Flush all indexes."""
        self.id_index.clear()
        self.provider_index.clear()
        self.service_index.clear()
        self.category_index.clear()
        self.tag_index.clear()
        self.alias_index.clear()
