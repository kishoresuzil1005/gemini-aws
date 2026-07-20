from typing import Optional

from .configuration import PipelineConfiguration
from .pipeline import ContextPipeline
from .registry import registry

class PipelineFactory:
    """Factory that creates a :class:`ContextPipeline`.

    If no explicit ``PipelineConfiguration`` is supplied, it builds a default one
    using the globally registered providers, a default ``MemoryCache`` and a
    ``ResourceResolver``.
    """

    def __init__(self, configuration: Optional[PipelineConfiguration] = None):
        self._external_config = configuration

    def create(self) -> ContextPipeline:
        """Return a ready‑to‑run ``ContextPipeline``.

        The configuration is resolved in the following order:
        1. Use the explicitly supplied ``PipelineConfiguration`` if provided.
        2. Otherwise, construct a configuration with:
           * providers = registry.ordered_providers
           * default cache, resolver, and strict mode from ``PipelineConfiguration`` defaults.
        """
        if self._external_config:
            config = self._external_config
        else:
            config = PipelineConfiguration(providers=registry.ordered_providers)
        return ContextPipeline(config)
