# knowledge/processing/pipeline.py
"""The Knowledge Processing Pipeline (M5, M6, M7) Orchestrator."""

import logging
from typing import List, Dict, Any
from pydantic import BaseModel

from .parsers.parser_registry import ParserRegistry
from .extractors.extractor_registry import ExtractorRegistry
from .normalizers.normalizer_registry import NormalizerRegistry

logger = logging.getLogger(__name__)


class KnowledgeProcessingPipeline:
    """Orchestrates the conversion of raw validated snapshots into Canonical Knowledge Models."""

    def __init__(self):
        self.parser_registry = ParserRegistry()
        self.extractor_registry = ExtractorRegistry()
        self.normalizer_registry = NormalizerRegistry()

    def process(self, raw_data: bytes, format_name: str, domain_category: str, context: Dict[str, Any]) -> List[BaseModel]:
        """Run the full processing pipeline on a validated snapshot.
        
        Args:
            raw_data: The raw bytes from content.json (or other format).
            format_name: "json", "yaml", "xml", "html", etc.
            domain_category: "security", "monitoring", etc.
            context: Snapshot context dictionary (e.g., {"connector_name": "cloudwatch_metrics"}).
            
        Returns:
            A list of instantiated Canonical Knowledge Models.
        """
        logger.info(f"Starting Knowledge Processing Pipeline for {domain_category} ({format_name})")
        
        # M5: Parsing
        parser = self.parser_registry.get_parser(format_name)
        logger.debug(f"Using {parser.name} to parse data.")
        parsed_data = parser.parse(raw_data)
        
        # M6: Extraction
        extractor = self.extractor_registry.get_extractor(domain_category)
        logger.debug(f"Using {extractor.name} to extract entities.")
        raw_entities = extractor.extract(parsed_data, context)
        
        # M7: Normalization
        normalizer = self.normalizer_registry.get_normalizer(domain_category)
        logger.debug(f"Using {normalizer.name} to normalize entities.")
        canonical_models = normalizer.normalize(raw_entities)
        
        logger.info(f"Pipeline completed successfully. Extracted {len(canonical_models)} canonical models.")
        return canonical_models
