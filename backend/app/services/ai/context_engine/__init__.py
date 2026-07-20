"""AI Context Engine – public API surface.

Typical usage::

    from app.services.ai.context_engine import ContextEngine, ContextRequest, ContextLevel

    engine = ContextEngine()
    context = await engine.build(
        ContextRequest(identifier="i-0abc123", level=ContextLevel.FULL)
    )

During application startup register the default providers::

    from app.services.ai.context_engine import register_default_providers
    register_default_providers()
"""

from .engine            import ContextEngine
from .request           import ContextRequest
from .enums             import ContextLevel, ProviderScope
from .models            import AIContext, ExecutionMetadata
from .registry          import registry, register_default_providers
from .base_provider     import BaseProvider
from .analysis_engine   import AnalysisEngine

__all__ = [
    "ContextEngine",
    "ContextRequest",
    "ContextLevel",
    "ProviderScope",
    "AIContext",
    "ExecutionMetadata",
    "BaseProvider",
    "AnalysisEngine",
    "registry",
    "register_default_providers",
]
