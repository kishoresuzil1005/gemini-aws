from typing import Any

from .configuration import PipelineConfiguration
from .pipeline import ContextPipeline
from .pipeline_factory import PipelineFactory
from .request import ContextRequest
from .models import AIContext

class ContextEngine:
    """Public entry point for building an :class:`AIContext`.

    The engine is deliberately thin – it validates the request, builds a
    ``ContextPipeline`` via :class:`PipelineFactory`, executes it, and returns the
    assembled context.
    """

    def __init__(
        self,
        container=None,
        configuration: PipelineConfiguration | None = None
    ):
        """Create a ContextEngine.

        Parameters
        ----------
        container: Optional[ServiceContainer]
            The dependency injection container. If not provided, a default one is created.
        configuration: Optional[PipelineConfiguration]
            If provided, this configuration will be used for every pipeline
            instance created by the engine. Otherwise, the default configuration
            (derived from the global ``registry``) is used.
        """
        from .service_container import ServiceContainer
        self.container = container or ServiceContainer.instance()
        self._factory = PipelineFactory(self.container, configuration)

    async def build(self, request: ContextRequest) -> AIContext:
        """Validate the request, run the pipeline, and return an ``AIContext``.

        The request is assumed to be a fully‑populated :class:`ContextRequest`
        instance. Minimal validation is performed here – the heavy lifting is
        delegated to the pipeline components.
        """
        # Basic validation – ``identifier`` must be non‑empty.
        if not request.identifier:
            raise ValueError("ContextRequest.identifier must be provided")
        # Create and run the pipeline.
        pipeline: ContextPipeline = self._factory.create()
        context: AIContext = await pipeline.run(request)
        return context
