# knowledge/extractors/extractor_registry.py
"""Registry for discovering and managing extractors."""

from typing import Dict, Type, Optional

from .base_extractor import BaseExtractor
from .extractor_exceptions import UnsupportedSourceError


class ExtractorRegistry:
    """Manages the mapping of provider/source to Extractors."""

    def __init__(self):
        # Maps (provider, source) to Extractor class
        self._extractors: Dict[str, Type[BaseExtractor]] = {}

    def register(self, provider: str, source: str, extractor_cls: Type[BaseExtractor]) -> None:
        key = f"{provider}:{source}".lower()
        self._extractors[key] = extractor_cls

    def get_extractor_class(self, provider: str, source: str) -> Type[BaseExtractor]:
        key = f"{provider}:{source}".lower()
        extractor_cls = self._extractors.get(key)
        if not extractor_cls:
            raise UnsupportedSourceError(f"No extractor registered for {provider}:{source}")
        return extractor_cls
