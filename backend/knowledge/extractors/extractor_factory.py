# knowledge/extractors/extractor_factory.py
"""Factory for instantiating the correct extractor."""

from typing import Type
import logging

from .base_extractor import BaseExtractor
from .extractor_registry import ExtractorRegistry
from .extractor_context import ExtractorContext

logger = logging.getLogger(__name__)


class ExtractorFactory:
    """Instantiates extractors based on context capability detection."""

    def __init__(self, registry: ExtractorRegistry):
        self.registry = registry

    def create_extractor(self, context: ExtractorContext) -> BaseExtractor:
        """Select and instantiate the appropriate extractor."""
        try:
            extractor_cls = self.registry.get_extractor_class(context.provider, context.source)
            return extractor_cls()
        except Exception as exc:
            logger.error("Failed to create extractor for %s:%s - %s", context.provider, context.source, exc)
            raise
