import pytest
from app.services.ai.context_engine.analyzers.dependency_analyzer import DependencyAnalyzer
from app.services.ai.context_engine.graph.graph_normalizer import GraphNormalizer
from app.services.ai.context_engine.models import AIContext

@pytest.fixture
def analyzer():
    return DependencyAnalyzer()

def create_context(resource_id, nodes, edges):
    # Pass it through the normalizer to simulate real behavior!
    raw = {
        "resource": {"resource_id": resource_id},
        "subgraph": {
            "nodes": nodes,
            "edges": edges
        }
    }
    normalized = GraphNormalizer.normalize(raw)
    
    return AIContext(
        resource={"resource_id": resource_id},
        graph=normalized
    )

def test_isolated_resource(analyzer):
    ctx = create_context("A", [{"id": "A"}], [])
    result = analyzer.analyze(ctx)
    assert result.metadata["is_isolated"] is True
    assert result.metadata["relationship_count"] == 0
    assert result.metadata["dependency_depth"] == 0
    
    findings = result.findings
    assert len(findings) == 1
    assert findings[0]["title"] == "Isolated Resource"

def test_single_dependency(analyzer):
    ctx = create_context("A", [{"id": "A"}, {"id": "B", "type": "Subnet"}], [{"source": "A", "target": "B", "relationship": "IN_SUBNET"}])
    result = analyzer.analyze(ctx)
    assert result.metadata["is_isolated"] is False
    assert result.metadata["relationship_count"] == 1
    assert result.metadata["dependency_depth"] == 1
    
    summary = result.metadata["dependency_summary"]
    assert "network" in summary
    assert "Subnet B" in summary["network"][0]

def test_multiple_dependencies(analyzer):
    nodes = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
    edges = [
        {"source": "A", "target": "B", "relationship": "USES_SG"},
        {"source": "A", "target": "C", "relationship": "ATTACHED_TO"}
    ]
    ctx = create_context("A", nodes, edges)
    result = analyzer.analyze(ctx)
    assert result.metadata["is_isolated"] is False
    assert result.metadata["relationship_count"] == 2
    
    summary = result.metadata["dependency_summary"]
    assert "security" in summary
    assert "storage" in summary

def test_duplicate_edges(analyzer):
    ctx = create_context("A", [{"id": "A"}, {"id": "B"}], [
        {"source": "A", "target": "B", "relationship": "USES_SG"},
        {"source": "A", "target": "B", "relationship": "USES_SG"}
    ])
    result = analyzer.analyze(ctx)
    # The edges are distinct in the graph (even if duplicates in content)
    assert result.metadata["relationship_count"] == 2
    # But connected resources should be 1
    assert result.metadata["connected_resource_count"] == 1

def test_cyclic_graph(analyzer):
    ctx = create_context("A", [{"id": "A"}, {"id": "B"}], [
        {"source": "A", "target": "B", "relationship": "PEERS_WITH"},
        {"source": "B", "target": "A", "relationship": "PEERS_WITH"}
    ])
    result = analyzer.analyze(ctx)
    assert result.metadata["relationship_count"] == 2
    assert result.metadata["dependency_depth"] == 1

def test_unknown_resource(analyzer):
    ctx = create_context("Unknown", [{"id": "X"}], [{"source": "X", "target": "Y", "relationship": "USES"}])
    result = analyzer.analyze(ctx)
    assert result.metadata["is_isolated"] is True

def test_malformed_graph(analyzer):
    ctx = create_context("A", ["this is just a string not a dict"], ["invalid edge string"])
    result = analyzer.analyze(ctx)
    # Normalizer will drop non-dict nodes/edges
    assert result.metadata["is_isolated"] is True

def test_normalized_graph(analyzer):
    # Test that normalizer converts weird formats
    ctx = create_context("A", 
        [{"_id": "A", "resource_type": "EC2"}], 
        [{"start": "A", "end": "B", "label": "IN_VPC"}]
    )
    result = analyzer.analyze(ctx)
    assert result.metadata["is_isolated"] is False
    assert result.metadata["relationship_count"] == 1
    assert "network" in result.metadata["dependency_summary"]

def test_bfs_dependency_depth(analyzer):
    # A -> B -> C -> D => Depth 3
    nodes = [{"id": "A"}, {"id": "B"}, {"id": "C"}, {"id": "D"}]
    edges = [
        {"source": "A", "target": "B", "relationship": "R"},
        {"source": "B", "target": "C", "relationship": "R"},
        {"source": "C", "target": "D", "relationship": "R"}
    ]
    ctx = create_context("A", nodes, edges)
    result = analyzer.analyze(ctx)
    assert result.metadata["dependency_depth"] == 3

def test_relationship_categories(analyzer):
    edges = [
        {"source": "A", "target": "B", "relationship": "USES_ROLE"}, # Security
        {"source": "A", "target": "C", "relationship": "MOUNTS"}, # Storage
        {"source": "A", "target": "D", "relationship": "ROUTES_TO"}, # Network
        {"source": "A", "target": "E", "relationship": "WEIRD_CUSTOM_REL"} # Infrastructure
    ]
    ctx = create_context("A", [{"id": "A"}, {"id": "B"}, {"id": "C"}, {"id": "D"}, {"id": "E"}], edges)
    result = analyzer.analyze(ctx)
    summary = result.metadata["dependency_summary"]
    
    assert "security" in summary
    assert "storage" in summary
    assert "network" in summary
    assert "infrastructure" in summary
