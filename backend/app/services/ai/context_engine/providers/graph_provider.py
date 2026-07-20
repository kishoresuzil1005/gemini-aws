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
    """Fetches raw graph topology from Neo4j (or MemoryGraphStore fallback)."""

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
            svc = self.neo4j_service

            # Get full graph from Neo4j
            full_graph = svc.get_graph()
            all_nodes: List[Dict] = full_graph.get("nodes", [])
            all_edges: List[Dict] = full_graph.get("edges", [])

            # Get root resource node
            root_node = svc.get_node(resource_id)
            root = {}
            if root_node:
                root = {
                    "id":       root_node.get("id", resource_id),
                    "name":     root_node.get("name", resource_id),
                    "type":     root_node.get("type", "Resource"),
                    "provider": root_node.get("provider", "aws"),
                    "region":   root_node.get("region", ""),
                    "status":   root_node.get("status", "unknown"),
                }

            # Build 1-hop subgraph
            connected_ids = {resource_id}
            subgraph_edges: List[Dict] = []
            for edge in all_edges:
                src = edge.get("source") or edge.get("from") or edge.get("a", {}).get("id", "")
                tgt = edge.get("target") or edge.get("to") or edge.get("b", {}).get("id", "")
                rel = edge.get("relation") or edge.get("type") or "CONNECTED"
                if src == resource_id or tgt == resource_id:
                    connected_ids.add(src)
                    connected_ids.add(tgt)
                    subgraph_edges.append({
                        "source": src,
                        "target": tgt,
                        "relation": rel,
                    })

            subgraph_nodes = [n for n in all_nodes if n.get("id") in connected_ids]

            return {
                "resource":  root,
                "subgraph": {
                    "nodes": subgraph_nodes,
                    "edges": subgraph_edges,
                },
            }

        except Exception as exc:
            logger.warning("GraphProvider failed for %s: %s", resource_id, exc)
            return self._fallback_from_memory(resource_id)

    def _fallback_from_memory(self, resource_id: str) -> Dict[str, Any]:
        try:
            from app.services.graph.neo4j_service import MemoryGraphStore
            nodes = [
                {"id": n["id"], "type": n["type"], "name": n["name"], "provider": n.get("provider", "aws")}
                for n in MemoryGraphStore.nodes.values()
            ]
            edges = [
                {"source": e["source"], "target": e["target"], "relation": e["type"]}
                for e in MemoryGraphStore.edges
            ]
            root = MemoryGraphStore.nodes.get(resource_id, {"id": resource_id, "name": resource_id})
            connected_ids = {resource_id}
            sub_edges = []
            for e in edges:
                if e["source"] == resource_id or e["target"] == resource_id:
                    connected_ids.add(e["source"])
                    connected_ids.add(e["target"])
                    sub_edges.append(e)
            sub_nodes = [n for n in nodes if n["id"] in connected_ids]
            return {
                "resource": root,
                "subgraph": {"nodes": sub_nodes, "edges": sub_edges},
            }
        except Exception:
            return {"resource": {}, "subgraph": {}}
