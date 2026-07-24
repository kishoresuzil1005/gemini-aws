# knowledge/normalization/normalization_registry.py
"""Registry for discovering and managing normalizers."""

from typing import Dict, Type

from .base_normalizer import BaseNormalizer
from .normalization_exceptions import UnsupportedProviderError

class NormalizationRegistry:
    """Manages the mapping of providers to their specific Normalizer implementations."""

    def __init__(self):
        # Maps provider -> Normalizer class
        # In this stub, we would map "aws", "azure", etc., to specific subclasses of BaseNormalizer
        self._normalizers: Dict[str, Type[BaseNormalizer]] = {}

    def register(self, provider: str, normalizer_cls: Type[BaseNormalizer]) -> None:
        self._normalizers[provider.lower()] = normalizer_cls

    def get_normalizer_class(self, provider: str) -> Type[BaseNormalizer]:
        normalizer_cls = self._normalizers.get(provider.lower())
        if not normalizer_cls:
            # Fallback to a generic normalizer if one were implemented, else error
            raise UnsupportedProviderError(f"No normalizer registered for provider: {provider}")
        return normalizer_cls
