# knowledge/normalization/quality_scorer.py
"""Calculates the normalization quality score."""

import logging
from typing import List

from .normalization_models import CanonicalModel
from ..extractors.knowledge_candidate import KnowledgeCandidate

logger = logging.getLogger(__name__)

class QualityScorer:
    """Evaluates consistency, coverage, and confidence of the normalized output."""

    def score(self, input_candidates: List[KnowledgeCandidate], output_models: List[CanonicalModel]) -> float:
        """Calculate a synthetic quality score for the normalization run."""
        
        if not input_candidates:
            return 0.0
            
        # Basic coverage metric: How many input non-relationship candidates yielded a model?
        non_rel_candidates = [c for c in input_candidates if c.__class__.__name__ != "RelationshipCandidate"]
        if not non_rel_candidates:
            return 100.0
            
        # Average input confidence
        avg_confidence = sum(c.confidence for c in non_rel_candidates) / len(non_rel_candidates)
        
        # Output ratio (simplified, assuming deduplication happened)
        # We just synthesize a score based on confidence and some structural assumptions
        completeness = min(100.0, (len(output_models) / len(non_rel_candidates)) * 100.0 * 1.5) # Allow deduplication shrinkage
        
        final_score = (avg_confidence * 100.0 + completeness) / 2.0
        return round(min(100.0, max(0.0, final_score)), 2)
