"""
Investigation Graph Builder — Phase 2
=======================================
Auto-expands a dependency graph from Neo4j starting at a root resource.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Set

from .session import InvestigationSession

logger = logging.getLogger(__name__)

_MAX_DEPTH = 3


class InvestigationGraphBuilder:
    """
    Queries Neo4j to build a directed dependency graph for the
    root resource, expanding up to MAX_DEPTH hops.
    """

    def __init__(self, max_depth: int = _MAX_DEPTH):
        self.max_depth = max_depth

    def build(self, session: InvestigationSession) -> Dict[str, List[str]]:
        """
        Expands the investigation graph from session.root_resource_id.
        Stores edges into session.dependency_graph and returns the graph.
        """
        if not session.root_resource_id:
            return {}

        try:
            from app.services.graph.neo4j_service import Neo4jService
            neo4j = Neo4jService()
            visited: Set[str] = set()
            self._expand(neo4j, session, session.root_resource_id, depth=0, visited=visited)
        except Exception as e:
            logger.warning("[GraphBuilder] Neo4j unavailable: %s", e)

        return session.dependency_graph

    def _expand(
        self,
        neo4j,
        session: InvestigationSession,
        resource_id: str,
        depth: int,
        visited: Set[str],
    ) -> None:
        if depth >= self.max_depth or resource_id in visited:
            return
        visited.add(resource_id)

        cypher = """
        MATCH (n:Resource {resource_id: $rid})-[r]->(m:Resource)
        RETURN m.resource_id AS target, type(r) AS rel_type
        LIMIT 20
        """
        try:
            records = neo4j.query(cypher, rid=resource_id)
            for rec in (records or []):
                target = rec.get("target")
                if target:
                    session.add_dependency(resource_id, target)
                    self._expand(neo4j, session, target, depth + 1, visited)
        except Exception as e:
            logger.debug("[GraphBuilder] Expand error for %s: %s", resource_id, e)
