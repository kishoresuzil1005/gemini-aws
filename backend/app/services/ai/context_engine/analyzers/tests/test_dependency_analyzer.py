import pytest
from app.services.ai.context_engine.analyzers.dependency_analyzer import DependencyAnalyzer
from app.services.ai.context_engine.models import AIContext

@pytest.fixture
def analyzer():
    return DependencyAnalyzer()

def create_context(resource_id, nodes, edges):
    return AIContext(
        resource={"resource_id": resource_id},
        graph={
            "resource": {"resource_id": resource_id},
            "subgraph": {
                "nodes": nodes,
                "edges": edges
            }
        }
    )

def test_isolated_resource(analyzer):
    ctx = create_context(
        resource_id="A",
        nodes=[{"id": "A"}],
        edges=[]
    )
    result = analyzer.analyze(ctx)
    assert result.metadata["is_isolated"] is True
    assert result.metadata["upstream_dependency_size"] == 0
    assert result.metadata["downstream_dependency_size"] == 0
    assert result.metadata["blast_radius_size"] == 0
    
    findings = result.findings
    assert len(findings) == 1
    assert findings[0]["title"] == "Isolated Resource"

def test_resource_with_one_dependency(analyzer):
    # A relies on B. A -> B (outgoing from A, so B is downstream of A)
    ctx = create_context(
        resource_id="A",
        nodes=[{"id": "A"}, {"id": "B"}],
        edges=[{"source": "A", "target": "B", "relation": "USES"}]
    )
    result = analyzer.analyze(ctx)
    assert result.metadata["is_isolated"] is False
    assert result.metadata["upstream_dependency_size"] == 0
    assert result.metadata["downstream_dependency_size"] == 1
    assert result.metadata["blast_radius_size"] == 1
    
    findings = result.findings
    assert len(findings) == 1
    assert findings[0]["title"] == "Blast Radius"

def test_resource_with_many_dependencies(analyzer):
    # A relies on B, C, D, E.
    ctx = create_context(
        resource_id="A",
        nodes=[{"id": "A"}, {"id": "B"}, {"id": "C"}, {"id": "D"}, {"id": "E"}],
        edges=[
            {"source": "A", "target": "B"},
            {"source": "A", "target": "C"},
            {"source": "A", "target": "D"},
            {"source": "A", "target": "E"},
            {"source": "A", "target": "B"} # Duplicate edge to same target to test unique blast radius
        ]
    )
    result = analyzer.analyze(ctx)
    assert result.metadata["is_isolated"] is False
    assert result.metadata["upstream_dependency_size"] == 0
    assert result.metadata["downstream_dependency_size"] == 5 # 5 outgoing edges
    assert result.metadata["blast_radius_size"] == 4 # 4 unique targets

def test_upstream_and_downstream(analyzer):
    # X -> A -> Y
    ctx = create_context(
        resource_id="A",
        nodes=[{"id": "X"}, {"id": "A"}, {"id": "Y"}],
        edges=[
            {"source": "X", "target": "A"},
            {"source": "A", "target": "Y"}
        ]
    )
    result = analyzer.analyze(ctx)
    assert result.metadata["is_isolated"] is False
    assert result.metadata["upstream_dependency_size"] == 1
    assert result.metadata["downstream_dependency_size"] == 1
    assert result.metadata["blast_radius_size"] == 1
    
    findings = result.findings
    assert len(findings) == 2 # Blast radius and Upstream Dependencies

def test_cyclic_graph(analyzer):
    # A -> B -> A
    ctx = create_context(
        resource_id="A",
        nodes=[{"id": "A"}, {"id": "B"}],
        edges=[
            {"source": "A", "target": "B"},
            {"source": "B", "target": "A"}
        ]
    )
    result = analyzer.analyze(ctx)
    assert result.metadata["is_isolated"] is False
    assert result.metadata["upstream_dependency_size"] == 1
    assert result.metadata["downstream_dependency_size"] == 1
    assert result.metadata["blast_radius_size"] == 1

def test_empty_graph(analyzer):
    ctx = create_context("A", [], [])
    result = analyzer.analyze(ctx)
    assert result.metadata["is_isolated"] is True
    assert result.metadata["upstream_dependency_size"] == 0
    assert result.metadata["downstream_dependency_size"] == 0
    assert result.metadata["blast_radius_size"] == 0

def test_unknown_resource(analyzer):
    # Resource ID is unknown, but graph has some edges
    ctx = create_context("Unknown", [{"id": "X"}], [{"source": "X", "target": "Y"}])
    result = analyzer.analyze(ctx)
    # The analyzer won't find incoming/outgoing for "Unknown" since the edges don't involve "Unknown"
    assert result.metadata["is_isolated"] is True
    assert result.metadata["upstream_dependency_size"] == 0
    assert result.metadata["downstream_dependency_size"] == 0
    assert result.metadata["blast_radius_size"] == 0

def test_critical_impact(analyzer):
    ctx = create_context(
        resource_id="A",
        nodes=[{"id": "A"}, {"id": "B", "type": "aws_lb"}],
        edges=[{"source": "A", "target": "B"}]
    )
    result = analyzer.analyze(ctx)
    assert result.metadata["blast_radius_size"] == 1
    findings = [f for f in result.findings if f["title"] == "Blast Radius"]
    assert findings[0]["severity"] == "CRITICAL"
    assert findings[0]["metadata"]["critical_impact_count"] == 1
