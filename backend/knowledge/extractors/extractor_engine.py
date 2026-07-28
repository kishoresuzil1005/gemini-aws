# knowledge/extractors/extractor_engine.py
"""The Extractor Engine orchestrates semantic extraction to generate candidates."""

import logging
import uuid
import time
from typing import Any, List

from .extractor_context import ExtractorContext
from .extractor_report import ExtractionReport
from .extractor_factory import ExtractorFactory
from .extractor_registry import ExtractorRegistry
from .knowledge_candidate import KnowledgeCandidate
from .extractor_exceptions import ExtractorError, PartialExtractionError

logger = logging.getLogger(__name__)


class ExtractorEngine:
    """Main orchestrator for generating structured Knowledge Candidates from intermediate documents."""

    def __init__(self):
        self.registry = ExtractorRegistry()
        # In a real system, we'd register specific extractors here
        self.factory = ExtractorFactory(self.registry)

    def process(self, parsed_data: Any, context: ExtractorContext) -> tuple[List[KnowledgeCandidate], ExtractionReport]:
        """Run extraction against parsed intermediate documents."""
        start_time = time.time()
        
        report = ExtractionReport(
            extraction_id=str(uuid.uuid4()),
            provider=context.provider,
            source=context.source,
            document_id=context.document_id
        )
        
        candidates: List[KnowledgeCandidate] = []
        
        try:
            extractor = self.factory.create_extractor(context)
            candidates = extractor.extract(parsed_data, context)
            
            # Aggregate stats
            report.entities_extracted = len(candidates)
            confidence_sum = 0.0
            
            for c in candidates:
                ctype = c.__class__.__name__
                report.candidate_counts[ctype] = report.candidate_counts.get(ctype, 0) + 1
                confidence_sum += c.confidence
                
                if ctype == "RelationshipCandidate":
                    report.relationships_found += 1
                    
            if candidates:
                report.average_confidence = confidence_sum / len(candidates)
                
        except PartialExtractionError as exc:
            logger.warning("Partial extraction for %s: %s", context.document_id, exc)
            report.warnings.append(str(exc))
        except ExtractorError as exc:
            logger.error("Extraction failed for %s: %s", context.document_id, exc)
            report.errors.append(str(exc))
        except Exception as exc:
            logger.exception("Unexpected extraction failure")
            report.errors.append(f"Unexpected error: {exc}")
            
        report.duration_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "Extraction complete for %s. Generated %d candidates in %d ms.",
            context.document_id, len(candidates), report.duration_ms
        )
        
        return candidates, report
