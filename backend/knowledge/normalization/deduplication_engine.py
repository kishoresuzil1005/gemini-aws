# knowledge/normalization/deduplication_engine.py
"""Identifies and safely merges duplicate canonical models."""

import logging
from typing import List, Dict

from .normalization_models import CanonicalModel

logger = logging.getLogger(__name__)

class DeduplicationEngine:
    """Safely merges overlapping canonical models."""

    def deduplicate(self, models: List[CanonicalModel]) -> List[CanonicalModel]:
        """Strip exact duplicates and merge metadata for colliding IDs."""
        merged: Dict[str, CanonicalModel] = {}
        duplicates_found = 0
        
        for model in models:
            cid = model.canonical_id
            if cid in merged:
                duplicates_found += 1
                # Merge metadata as a simple resolution strategy
                existing = merged[cid]
                existing.metadata.update(model.metadata)
                
                # Merge tags
                existing.tags.update(model.tags)
            else:
                merged[cid] = model
                
        if duplicates_found > 0:
            logger.debug(f"Deduplication removed/merged {duplicates_found} overlapping entities.")
            
        return list(merged.values())
