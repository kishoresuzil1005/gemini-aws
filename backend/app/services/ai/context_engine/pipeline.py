from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

from .models import AIContext, ExecutionMetadata
from .assembler import ContextAssembler
from .provider_manager import ProviderManager
from .configuration import PipelineConfiguration
from .request import ContextRequest

class ContextPipeline:
    """Orchestrates the end‑to‑end flow for building an :class:`AIContext`.

    Steps (in order):
    1. Resolve the incoming request identifier to a canonical resource.
    2. Run the ``ProviderManager`` to execute providers (with caching).
    3. Assemble the raw payloads into an :class:`AIContext`.
    4. Return the assembled context.
    """

    def __init__(self, config: PipelineConfiguration, container=None):
        self.config = config
        self.container = container
        # Lazy initialisation of components – they can be swapped later.
        self._assembler = ContextAssembler()
        self._provider_manager = ProviderManager(
            providers=self.config.providers,
            cache=self.config.cache,
            strict=self.config.strict,
        )

    async def run(self, request: ContextRequest) -> AIContext:
        # Resolve the identifier to a resource.
        resolved = await self.config.resolver.resolve_identifier(request)

        # Prepare execution metadata.
        exec_meta = ExecutionMetadata()

        # Execute providers (caching handled inside ProviderManager).
        payloads: Dict[str, Any] = await self._provider_manager.run(resolved, request, exec_meta)

        # Mark execution complete (captures end_time and duration).
        exec_meta.mark_complete()

        # Assemble the final AIContext.
        context = self._assembler.assemble(payloads, exec_meta, level=request.level)
        print("===== AIContext =====")
        print(f"Resource: {context.resource}")
        print(f"Graph: {context.graph}")
        print(f"Security: {context.security}")
        print(f"Metrics: {context.metrics}")
        print("===== Cost =====")
        print(f"Cost: {context.cost}")

        return context
