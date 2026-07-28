# knowledge/normalization/normalization_engine.py
"""The Normalization Engine orchestrates the mapping of Candidates to Canonical Models."""

import logging
import uuid
import time
from typing import List

from .normalization_context import NormalizationContext
from .normalization_report import NormalizationReport
from .normalization_factory import NormalizationFactory
from .normalization_registry import NormalizationRegistry
from .normalization_models import CanonicalModel
from .relationship_resolver import RelationshipResolver
from .deduplication_engine import DeduplicationEngine
from .quality_scorer import QualityScorer
from .normalization_exceptions import NormalizationError, PartialNormalizationError
from ..extractors.knowledge_candidate import KnowledgeCandidate

logger = logging.getLogger(__name__)


class NormalizationEngine:
    """Main orchestrator for mapping provider-specific knowledge into the multi-cloud canonical format."""

    def __init__(self):
        self.registry = NormalizationRegistry()
        self.factory = NormalizationFactory(self.registry)
        self.relationship_resolver = RelationshipResolver()
        self.dedup_engine = DeduplicationEngine()
        self.quality_scorer = QualityScorer()

    def process(self, candidates: List[KnowledgeCandidate], context: NormalizationContext) -> tuple[List[CanonicalModel], NormalizationReport]:
        """Run normalization against extracted candidates."""
        start_time = time.time()
        
        report = NormalizationReport(
            normalization_id=str(uuid.uuid4()),
            provider=context.provider,
            source=context.source,
            document_id=context.document_id
        )
        
        canonical_models: List[CanonicalModel] = []
        relationships = [c for c in candidates if c.__class__.__name__ == "RelationshipCandidate"]
        
        try:
            # 1. Normalizer Selection
            normalizer = self.factory.create_normalizer(context)
            
            # 2. Canonical Mapping
            raw_models = normalizer.normalize(candidates, context)
            
            # 3. Deduplication
            canonical_models = self.dedup_engine.deduplicate(raw_models)
            report.duplicates_removed = len(raw_models) - len(canonical_models)
            
            # 4. Relationship Resolution
            canonical_models = self.relationship_resolver.resolve(canonical_models, relationships)
            report.relationships_resolved = len(relationships) # simplified for reporting
            
            # 5. Reporting Stats
            report.entities_normalized = len(canonical_models)
            for m in canonical_models:
                mtype = m.__class__.__name__
                report.model_counts[mtype] = report.model_counts.get(mtype, 0) + 1
                
            # 6. Quality Scoring
            report.quality_score = self.quality_scorer.score(candidates, canonical_models)
                
        except PartialNormalizationError as exc:
            logger.warning("Partial normalization for %s: %s", context.document_id, exc)
            report.warnings.append(str(exc))
        except NormalizationError as exc:
            logger.error("Normalization failed for %s: %s", context.document_id, exc)
            report.errors.append(str(exc))
        except Exception as exc:
            logger.exception("Unexpected normalization failure")
            report.errors.append(f"Unexpected error: {exc}")
            
        report.duration_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "Normalization complete for %s. Generated %d canonical models in %d ms.",
            context.document_id, len(canonical_models), report.duration_ms
        )
        
        return canonical_models, report
