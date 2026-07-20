"""PipelineConfiguration – holds all components needed to build a ContextPipeline.

Pydantic is not used here because the configuration holds arbitrary objects
(provider instances, cache backends, resolver).  A plain dataclass keeps things
simple and avoids schema‑generation errors for arbitrary types.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .base_provider import BaseProvider
from .cache import MemoryCache, CacheBackend
from .resolver import ResourceResolver


@dataclass
class PipelineConfiguration:
    """Configuration for building a :class:`~pipeline.ContextPipeline`.

    Attributes
    ----------
    providers:
        Ordered list of provider instances to run.  If empty the pipeline
        will return an empty :class:`~models.AIContext`.
    cache:
        Cache backend used by :class:`~provider_manager.ProviderManager`.
        Defaults to an in‑memory cache.
    resolver:
        Component that resolves resource identifiers to
        :class:`~resolved_resource.ResolvedResource` objects.
    strict:
        If ``True``, the first provider failure raises
        :class:`~exceptions.ProviderError` and aborts the pipeline.
        If ``False``, failures are recorded and execution continues.
    """

    providers: List[BaseProvider] = field(default_factory=list)
    cache: CacheBackend = field(default_factory=MemoryCache)
    resolver: ResourceResolver = field(default_factory=ResourceResolver)
    strict: bool = True
