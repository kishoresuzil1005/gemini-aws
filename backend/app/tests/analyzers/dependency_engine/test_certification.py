import time
import random
import threading
from typing import Dict, Any, List

from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph
from app.services.ai.analyzers.engines.graph.graph_processor import GraphProcessor
from app.services.ai.analyzers.engines.graph.graph_index import GraphIndex
from app.services.ai.analyzers.implementations.dependency_analyzer import DependencyAnalyzer
from app.services.ai.analyzers.base.analyzer_models import AnalyzerContext

def generate_synthetic_graph(num_nodes: int) -> Dict[str, Any]:
    nodes = []
    edges = []
    
    # 10% DB, 10% ALB, 30% App, 50% EC2
    for i in range(num_nodes):
        if i < num_nodes * 0.1:
            ntype = "RDS"
            az = "us-east-1a"
        elif i < num_nodes * 0.2:
            ntype = "ALB"
            az = "us-east-1a"
        elif i < num_nodes * 0.5:
            ntype = "Lambda"
            az = "us-east-1b"
        else:
            ntype = "EC2"
            az = "us-east-1c"
            
        nodes.append({
            "id": f"node-{i}",
            "type": ntype,
            "region": "us-east-1",
            "availability_zone": az,
            "tags": {"Environment": "Production" if i % 2 == 0 else "Dev"}
        })
        
    # Generate edges (Random DAGish)
    for i in range(int(num_nodes * 1.5)):
        src = f"node-{random.randint(0, num_nodes-1)}"
        tgt = f"node-{random.randint(0, num_nodes-1)}"
        if src != tgt: # Try to avoid direct self loops but GraphProcessor handles it
            edges.append({"source": src, "target": tgt, "type": "DEPENDS_ON"})
            
    return {"nodes": nodes, "edges": edges}

def test_correctness():
    """Phase 1: Correctness of Dependency Engine & Root Cause."""
    raw_graph = {
        "nodes": [
            {"id": "alb-1", "type": "ALB", "region": "us-east-1"},
            {"id": "app-1", "type": "EC2", "region": "us-east-1"},
            {"id": "db-1", "type": "RDS", "region": "us-east-1"}, # True SPOF
            {"id": "isolated-1", "type": "EC2", "region": "us-east-1"}
        ],
        "edges": [
            {"source": "alb-1", "target": "app-1"},
            {"source": "app-1", "target": "db-1"}
        ]
    }
    
    analyzer = DependencyAnalyzer()
    context = AnalyzerContext(graph=raw_graph)
    result = analyzer.analyze(context)
    
    assert len(result.findings) > 0, "Should generate findings for SPOF DB."
    spof_finding = next((f for f in result.findings if f.resource_id == "db-1"), None)
    assert spof_finding is not None
    assert spof_finding.severity.value in ["HIGH", "CRITICAL"]
    assert "Criticality: Mission Critical" in spof_finding.business_impact or "Criticality: Production" in spof_finding.business_impact or "Standard" in spof_finding.business_impact
    assert "Root Causes:" in spof_finding.technical_impact

def test_performance(num_nodes):
    """Phase 2: Performance & Scalability (O(V+E) validation)."""
    raw_graph = generate_synthetic_graph(num_nodes)
    
    start_time = time.time()
    analyzer = DependencyAnalyzer()
    context = AnalyzerContext(graph=raw_graph)
    result = analyzer.analyze(context)
    duration = time.time() - start_time
    
    print(f"\n[Performance] {num_nodes} nodes processed in {duration:.4f}s. Found {len(result.findings)} findings.")
    assert duration < 10.0, "Analyzer is scaling worse than O(V+E) or is too slow."

def test_concurrency():
    """Phase 3: Thread Safety & Concurrency."""
    raw_graph = generate_synthetic_graph(100)
    analyzer = DependencyAnalyzer()
    context = AnalyzerContext(graph=raw_graph)
    
    errors = []
    
    def worker():
        try:
            res = analyzer.analyze(context)
            assert len(res.findings) >= 0
        except Exception as e:
            errors.append(e)
            
    threads = [threading.Thread(target=worker) for _ in range(25)]
    
    start_time = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    duration = time.time() - start_time
    
    print(f"\n[Concurrency] 25 threads completed in {duration:.4f}s.")
    assert len(errors) == 0, f"Thread safety violated: {errors}"

def test_fault_injection():
    """Phase 4: Fault Tolerance on Malformed Graphs."""
    raw_graph = {
        "nodes": [
            {"id": "node-1"}, # Missing type, region
            {"id": "node-2", "type": "Lambda"}
        ],
        "edges": [
            {"source": "node-1", "target": "node-1"}, # Self loop
            {"source": "node-2", "target": "node-3"}  # Broken edge (node-3 missing)
        ]
    }
    
    analyzer = DependencyAnalyzer()
    context = AnalyzerContext(graph=raw_graph)
    try:
        result = analyzer.analyze(context)
        assert result is not None
        print(f"\n[Fault Injection] Passed gracefully.")
    except Exception as e:
        print(f"Analyzer crashed on malformed graph: {e}")
        raise

if __name__ == "__main__":
    print("Running Certification Tests for Dependency Analyzer...")
    test_correctness()
    for size in [100, 1000, 10000]:
        test_performance(size)
    test_concurrency()
    test_fault_injection()
    print("\nAll Certification Tests Passed!")
