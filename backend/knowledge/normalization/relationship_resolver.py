# knowledge/normalization/relationship_resolver.py
"""Resolves relationships across the normalized payload."""

import logging
from typing import List, Dict

from .normalization_models import CanonicalModel
from ..extractors.relationship_candidate import RelationshipCandidate

logger = logging.getLogger(__name__)

class RelationshipResolver:
    """Ensures parent/child/alias linkages are resolved."""

    def resolve(self, models: List[CanonicalModel], relationships: List[RelationshipCandidate]) -> List[CanonicalModel]:
        """Applies relationship linkages to the canonical models where applicable.
        
        In a full implementation, this might augment the models' metadata with edges.
        For this design milestone, we log the resolution.
        """
        # Create an index of models by canonical_id
        model_index = {m.canonical_id: m for m in models}
        resolved_count = 0
        
        for rel in relationships:
            source = rel.source_entity
            target = rel.target_entity
            if source in model_index and target in model_index:
                # E.g., add to a 'related' list in metadata
                source_model = model_index[source]
                if "related_to" not in source_model.metadata:
                    source_model.metadata["related_to"] = []
                source_model.metadata["related_to"].append({
                    "id": target,
                    "type": rel.relationship_type
                })
                resolved_count += 1
                
        logger.debug(f"Resolved {resolved_count} relationship edges across canonical models.")
        return models
