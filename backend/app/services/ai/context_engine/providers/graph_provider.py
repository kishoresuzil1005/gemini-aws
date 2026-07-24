"""GraphProvider – fetches raw graph topology from Neo4j.

Uses the existing ``Neo4jService`` to query nodes and edges for the given
resource, including its direct neighborhood (1-hop subgraph).

Returns only topology data – no analysis (criticality, blast-radius, paths).

Lookup strategy
---------------
1. Try ``resource.resource_id`` (authoritative DB id, e.g. "db-xxxx").
2. If Neo4j returns empty, try ``resource.resource_name`` (human name, e.g. "cloudops-db").
3. If still empty, try the ``original_identifier`` typed by the user.
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
        data = self._fetch_topology(resource)
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)

    # ------------------------------------------------------------------

    def _fetch_topology(self, resource: ResolvedResource) -> Dict[str, Any]:
        """Try each candidate ID until Neo4j returns a non-empty subgraph."""
        # Build list of IDs to attempt (deduplicated, preserving priority order)
        candidates: List[str] = []
        for val in [
            resource.resource_id,
            resource.resource_name,
            resource.original_identifier,
        ]:
            if val and val not in candidates:
                candidates.append(val)

        for candidate_id in candidates:
            result = self._query_neo4j(candidate_id)
            # Non-empty means we found the node in Neo4j
            if result.get("resource") or result.get("subgraph", {}).get("nodes"):
                logger.info(
                    "GraphProvider: found graph data for '%s' using key '%s'",
                    resource.original_identifier,
                    candidate_id,
                )
                return result

        # No match – return empty structure
        logger.warning(
            "GraphProvider: no graph data found for '%s' (tried: %s)",
            resource.original_identifier,
            candidates,
        )
        return {
            "resource": {},
            "subgraph": {"nodes": [], "edges": []},
            "upstream": [],
            "downstream": [],
        }

    def _query_neo4j(self, resource_id: str) -> Dict[str, Any]:
        try:
            subgraph_data = self.neo4j_service.get_resource_subgraph(resource_id)
            return subgraph_data

        except Exception as exc:
            logger.warning("GraphProvider._query_neo4j(%s) failed: %s", resource_id, exc)
            return {
                "resource": {},
                "subgraph": {"nodes": [], "edges": []},
                "upstream": [],
                "downstream": [],
            }
