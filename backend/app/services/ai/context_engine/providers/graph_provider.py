"""GraphProvider – fetches raw graph topology from Neo4j.

Uses the existing ``Neo4jService`` to query nodes and edges for the given
resource, including its direct neighborhood (1-hop subgraph).

Returns only topology data – no analysis (criticality, blast-radius, paths).
"""

import time
import logging
from typing import Any, Dict, List

from ..base_provider import BaseProvider
from ..common.constants import GRAPH_PROVIDER_ENABLED, TTL_STATIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)


class GraphProvider(BaseProvider):
    """Fetches raw graph topology from Neo4j."""

    name       = "graph"
    scope      = ProviderScope.STATIC
    priority   = 10
    output_key = "graph"
    cache_ttl  = TTL_STATIC
    version    = "1.0"
    source     = "neo4j"
    enabled    = flag_enabled(GRAPH_PROVIDER_ENABLED)

    def __init__(self, *, neo4j_service):
        super().__init__()
        self.neo4j_service = neo4j_service

    def supports(self, level: ContextLevel) -> bool:
        return True   # graph topology is needed at every context level

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        data = self._fetch_topology(resource.resource_id)
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)

    # ------------------------------------------------------------------

    def _fetch_topology(self, resource_id: str) -> Dict[str, Any]:
        try:
            return self.neo4j_service.get_resource_subgraph(resource_id)

        except Exception as exc:
            logger.warning("GraphProvider failed for %s: %s", resource_id, exc)
            return {
                "resource": {},
                "subgraph": {"nodes": [], "edges": []}
            }
