"""RelationshipAnalyzer – derives relationship insights from the graph topology.

This analyzer operates on the ``graph`` section of :class:`~models.AIContext`
(populated by :class:`~providers.graph_provider.GraphProvider`) and exposes a
set of traversal methods used by other analyzers and services.

**No Neo4j queries are made here** – all computations are done in‑memory using
the topology already assembled in ``AIContext.graph``.

Available methods
-----------------
* :meth:`get_downstream`            – resources that depend on the given node.
* :meth:`get_upstream`              – resources the given node depends on.
* :meth:`compute_blast_radius`      – set of nodes affected if the given node fails.
* :meth:`shortest_path`             – shortest connection between two nodes.
* :meth:`detect_cycles`             – identify circular dependencies.
* :meth:`dependency_depth`          – max depth of the dependency tree.
* :meth:`reachable_nodes`           – all nodes reachable from a given node.
* :meth:`find_single_points_of_failure` – nodes whose removal disconnects the graph.
"""

from typing import Any, Dict, List, Optional, Set

from .base_analyzer import BaseAnalyzer
from ..models import AIContext, AnalyzerResult


class RelationshipAnalyzer(BaseAnalyzer):
    """Traversal‑based relationship analysis using AIContext.graph topology."""

    name = "relationship"

    def analyze(self, context: AIContext) -> AnalyzerResult:
        """Run all relationship analyses and return a combined summary."""
        root_id = context.resource.get("id", "")
        return AnalyzerResult(
            status="success",
            analyzer=self.name,
            metadata={
                "downstream":                self.get_downstream(context, root_id),
                "upstream":                  self.get_upstream(context, root_id),
                "blast_radius":              self.compute_blast_radius(context, root_id),
                "cycles":                    self.detect_cycles(context),
                "dependency_depth":          self.dependency_depth(context, root_id),
                "reachable_nodes":           self.reachable_nodes(context, root_id),
                "single_points_of_failure":  self.find_single_points_of_failure(context),
            },
        )

    # ------------------------------------------------------------------
    #  Traversal helpers
    # ------------------------------------------------------------------

    def get_downstream(self, context: AIContext, node_id: str) -> List[str]:
        """Return IDs of nodes that depend on *node_id* (children)."""
        graph = context.graph
        edges = graph.get("edges", [])
        return [
            e.get("target") for e in edges
            if e.get("source") == node_id and e.get("target")
        ]

    def get_upstream(self, context: AIContext, node_id: str) -> List[str]:
        """Return IDs of nodes that *node_id* depends on (parents)."""
        graph = context.graph
        edges = graph.get("edges", [])
        return [
            e.get("source") for e in edges
            if e.get("target") == node_id and e.get("source")
        ]

    def compute_blast_radius(self, context: AIContext, node_id: str) -> List[str]:
        """Return all node IDs that would be affected if *node_id* fails.

        Performs a BFS/DFS from *node_id* following downstream edges.
        """
        visited: Set[str] = set()
        queue   = [node_id]
        while queue:
            current = queue.pop()
            for child in self.get_downstream(context, current):
                if child not in visited:
                    visited.add(child)
                    queue.append(child)
        visited.discard(node_id)
        return list(visited)

    def shortest_path(
        self,
        context: AIContext,
        source_id: str,
        target_id: str,
    ) -> Optional[List[str]]:
        """Return the shortest path from *source_id* to *target_id*, or ``None``."""
        from collections import deque
        graph  = context.graph
        edges  = graph.get("edges", [])
        adj: Dict[str, List[str]] = {}
        for e in edges:
            adj.setdefault(e.get("source", ""), []).append(e.get("target", ""))

        queue: deque = deque([[source_id]])
        visited: Set[str] = {source_id}
        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == target_id:
                return path
            for neighbour in adj.get(node, []):
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(path + [neighbour])
        return None

    def detect_cycles(self, context: AIContext) -> List[List[str]]:
        """Detect circular dependencies in the graph.

        Returns a list of cycles (each cycle is a list of node IDs).
        Uses DFS with a recursion‑stack colour‑marking approach.
        """
        graph = context.graph
        edges = graph.get("edges", [])
        adj: Dict[str, List[str]] = {}
        for e in edges:
            adj.setdefault(e.get("source", ""), []).append(e.get("target", ""))

        WHITE, GRAY, BLACK = 0, 1, 2
        colour: Dict[str, int] = {}
        cycles: List[List[str]] = []
        stack: List[str] = []

        def dfs(node: str) -> None:
            colour[node] = GRAY
            stack.append(node)
            for neighbour in adj.get(node, []):
                if colour.get(neighbour) == GRAY:
                    # Found a cycle; extract it from the stack.
                    idx   = stack.index(neighbour)
                    cycles.append(list(stack[idx:]))
                elif colour.get(neighbour, WHITE) == WHITE:
                    dfs(neighbour)
            stack.pop()
            colour[node] = BLACK

        nodes = {e.get("source") for e in edges} | {e.get("target") for e in edges}
        for n in nodes:
            if n and colour.get(n, WHITE) == WHITE:
                dfs(n)

        return cycles

    def dependency_depth(self, context: AIContext, node_id: str) -> int:
        """Return the maximum depth of the dependency tree rooted at *node_id*."""
        visited: Set[str] = set()

        def _depth(n: str) -> int:
            if n in visited:
                return 0
            visited.add(n)
            children = self.get_downstream(context, n)
            return 1 + max((_depth(c) for c in children), default=0)

        return _depth(node_id)

    def reachable_nodes(self, context: AIContext, node_id: str) -> List[str]:
        """Return all node IDs reachable from *node_id* (any direction)."""
        visited: Set[str] = set()
        queue   = [node_id]
        while queue:
            current = queue.pop()
            visited.add(current)
            for child in self.get_downstream(context, current):
                if child not in visited:
                    queue.append(child)
            for parent in self.get_upstream(context, current):
                if parent not in visited:
                    queue.append(parent)
        visited.discard(node_id)
        return list(visited)

    def find_single_points_of_failure(self, context: AIContext) -> List[str]:
        """Identify nodes whose removal would disconnect part of the graph.

        Uses a simplified articulation‑point algorithm.  Returns a list of
        node IDs that are single points of failure.

        Useful for:
        * High‑Availability reviews
        * Well‑Architected reviews
        * Disaster Recovery planning
        * Resilience scoring
        """
        graph = context.graph
        edges = graph.get("edges", [])
        if not edges:
            return []

        # Build an undirected adjacency list
        adj: Dict[str, Set[str]] = {}
        for e in edges:
            src, tgt = e.get("source", ""), e.get("target", "")
            if src and tgt:
                adj.setdefault(src, set()).add(tgt)
                adj.setdefault(tgt, set()).add(src)

        nodes     = list(adj.keys())
        visited:  Dict[str, bool]  = {}
        disc:     Dict[str, int]   = {}
        low:      Dict[str, int]   = {}
        parent:   Dict[str, Optional[str]] = {}
        ap:       Set[str]         = set()
        timer     = [0]

        def _dfs(u: str) -> None:
            visited[u] = True
            disc[u] = low[u] = timer[0]
            timer[0] += 1
            child_count = 0
            for v in adj.get(u, set()):
                if not visited.get(v):
                    parent[v] = u
                    child_count += 1
                    _dfs(v)
                    low[u] = min(low[u], low[v])
                    # u is an articulation point if:
                    #  (a) u is root and has 2+ children
                    #  (b) u is not root and low[v] >= disc[u]
                    if parent.get(u) is None and child_count > 1:
                        ap.add(u)
                    if parent.get(u) is not None and low[v] >= disc[u]:
                        ap.add(u)
                elif v != parent.get(u):
                    low[u] = min(low[u], disc[v])

        for n in nodes:
            if not visited.get(n):
                parent[n] = None
                _dfs(n)

        return list(ap)
