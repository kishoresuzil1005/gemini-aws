"""Unit tests for RelationshipAnalyzer."""

import pytest
from ..relationship_analyzer import RelationshipAnalyzer
from ...models import AIContext


def _make_context(nodes=None, edges=None, resource_id="node-A"):
    """Helper to build a minimal AIContext with graph topology."""
    ctx = AIContext()
    ctx.resource = {"id": resource_id}
    ctx.graph = {
        "nodes": nodes or [],
        "edges": edges or [],
    }
    return ctx


@pytest.fixture
def analyzer():
    return RelationshipAnalyzer()


class TestRelationshipAnalyzer:
    """Core traversal method tests."""

    def test_get_downstream_empty(self, analyzer):
        ctx = _make_context()
        assert analyzer.get_downstream(ctx, "node-A") == []

    def test_get_downstream(self, analyzer):
        edges = [{"source": "A", "target": "B"}, {"source": "A", "target": "C"}]
        ctx   = _make_context(edges=edges)
        result = analyzer.get_downstream(ctx, "A")
        assert set(result) == {"B", "C"}

    def test_get_upstream(self, analyzer):
        edges = [{"source": "A", "target": "B"}, {"source": "C", "target": "B"}]
        ctx   = _make_context(edges=edges)
        result = analyzer.get_upstream(ctx, "B")
        assert set(result) == {"A", "C"}

    def test_blast_radius(self, analyzer):
        # A → B → C;  blast_radius(A) should include B and C
        edges = [{"source": "A", "target": "B"}, {"source": "B", "target": "C"}]
        ctx   = _make_context(edges=edges, resource_id="A")
        result = analyzer.compute_blast_radius(ctx, "A")
        assert set(result) == {"B", "C"}

    def test_shortest_path_exists(self, analyzer):
        edges = [{"source": "A", "target": "B"}, {"source": "B", "target": "C"}]
        ctx   = _make_context(edges=edges)
        path  = analyzer.shortest_path(ctx, "A", "C")
        assert path == ["A", "B", "C"]

    def test_shortest_path_none(self, analyzer):
        ctx  = _make_context()
        path = analyzer.shortest_path(ctx, "X", "Y")
        assert path is None

    def test_detect_cycles_empty(self, analyzer):
        ctx    = _make_context()
        cycles = analyzer.detect_cycles(ctx)
        assert cycles == []

    def test_detect_cycles_found(self, analyzer):
        # A → B → A is a cycle
        edges  = [{"source": "A", "target": "B"}, {"source": "B", "target": "A"}]
        ctx    = _make_context(edges=edges)
        cycles = analyzer.detect_cycles(ctx)
        assert len(cycles) > 0

    def test_dependency_depth(self, analyzer):
        edges = [{"source": "A", "target": "B"}, {"source": "B", "target": "C"}]
        ctx   = _make_context(edges=edges)
        depth = analyzer.dependency_depth(ctx, "A")
        assert depth == 3   # A(1) → B(2) → C(3)

    def test_reachable_nodes(self, analyzer):
        edges = [{"source": "A", "target": "B"}, {"source": "B", "target": "C"}]
        ctx   = _make_context(edges=edges)
        nodes = analyzer.reachable_nodes(ctx, "A")
        assert set(nodes) == {"B", "C"}

    def test_single_points_of_failure_empty(self, analyzer):
        ctx = _make_context()
        assert analyzer.find_single_points_of_failure(ctx) == []

    def test_single_points_of_failure_found(self, analyzer):
        # A - B - C  (linear chain; B is the articulation point)
        edges = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
        ]
        ctx  = _make_context(edges=edges)
        spof = analyzer.find_single_points_of_failure(ctx)
        assert "B" in spof
