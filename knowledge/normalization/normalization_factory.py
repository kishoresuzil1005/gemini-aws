# knowledge/normalization/normalization_factory.py
"""Factory for instantiating the correct normalizer."""

import logging
from typing import Type

from .base_normalizer import BaseNormalizer
from .normalization_registry import NormalizationRegistry
from .normalization_context import NormalizationContext

logger = logging.getLogger(__name__)

class NormalizationFactory:
    """Instantiates normalizers based on provider capabilities."""

    def __init__(self, registry: NormalizationRegistry):
        self.registry = registry

    def create_normalizer(self, context: NormalizationContext) -> BaseNormalizer:
        """Select and instantiate the appropriate normalizer."""
        try:
            normalizer_cls = self.registry.get_normalizer_class(context.provider)
            return normalizer_cls()
        except Exception as exc:
            logger.error("Failed to create normalizer for provider %s: %s", context.provider, exc)
            raise
