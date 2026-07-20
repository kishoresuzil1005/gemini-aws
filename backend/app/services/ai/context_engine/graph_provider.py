import os
from typing import Dict, Any, List

from .base_provider import BaseProvider
from .enums import ProviderScope, ContextLevel
from .resolved_resource import ResolvedResource
from .request import ContextRequest

class GraphProvider(BaseProvider):
    """Collect raw graph topology data (nodes, edges, subgraph).
    No analysis (criticality, blast radius, paths) is performed here – those
    belong to separate analyzer components.
    """

    name = "graph"
    scope = ProviderScope.FULL
    priority = 0
    output_key = "graph"
    enabled = os.getenv("ENABLE_GRAPH_PROVIDER", "true").lower() == "true"

    def supports(self, level: ContextLevel) -> bool:
        # Graph data is useful for all context levels.
        return True

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        # Stub implementation – replace with actual Neo4j queries.
        # For demonstration we return empty structures.
        return {
            "nodes": [],  # List of node dicts
            "edges": [],  # List of edge dicts
            "subgraph": {},  # Optional filtered sub‑graph
        }
