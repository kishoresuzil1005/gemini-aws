# knowledge/relationships/relationship_builder.py
"""Extracts edges from Canonical Models and builds entries."""

import logging
import uuid
from typing import List

from .relationship_models import CanonicalRelationship
from .relationship_classifier import RelationshipClassifier
from .relationship_validator import RelationshipValidator
from .relationship_resolver import RelationshipResolver
from ..catalog.catalog_models import CanonicalResource

logger = logging.getLogger(__name__)

class RelationshipBuilder:
    """Consumes M7/M8 Canonical Models and constructs the CanonicalRelationships."""

    def __init__(self):
        self.classifier = RelationshipClassifier()
        self.validator = RelationshipValidator()
        self.resolver = RelationshipResolver()

    def build(self, resources: List[CanonicalResource]) -> List[CanonicalRelationship]:
        """Extract all static relationship pointers and convert them into managed edges."""
        raw_relationships: List[CanonicalRelationship] = []
        valid_nodes = set(r.resource_id for r in resources)
        
        for res in resources:
            # We assume M7 placed pointers in `res.relationships` like: 
            # [{"id": "arn:aws:vpc", "type": "attached_to"}]
            for ptr in res.relationships:
                rel_type = self.classifier.classify(ptr.get("type", "unknown"))
                target_id = ptr.get("id")
                
                if not target_id:
                    continue
                    
                edge = CanonicalRelationship(
                    relationship_id=str(uuid.uuid4()),
                    relationship_type=rel_type,
                    source_resource_id=res.resource_id,
                    target_resource_id=target_id,
                    provider=res.provider,
                    service=res.service
                )
                raw_relationships.append(edge)
                
        # Resolve (strip dangling) and Validate (detect cycles)
        resolved_relationships = self.resolver.resolve(raw_relationships, valid_nodes)
        final_relationships = self.validator.validate(resolved_relationships)
        
        logger.info(f"Built {len(final_relationships)} validated CanonicalRelationships.")
        return final_relationships
