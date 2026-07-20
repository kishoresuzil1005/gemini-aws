from datetime import datetime
from .request import ContextRequest
from .resolved_resource import ResolvedResource
from .exceptions import ResourceNotFoundError

class ResourceResolver:
    """Resolves any identifier to a canonical ``resource_id``.
    Method name ``resolve_identifier`` leaves room for future specialised resolvers.
    """

    async def resolve_identifier(self, request: ContextRequest) -> ResolvedResource:
        if not request.identifier:
            raise ResourceNotFoundError("Identifier cannot be empty")
        return ResolvedResource(resource_id=request.identifier, original_identifier=request.identifier)
