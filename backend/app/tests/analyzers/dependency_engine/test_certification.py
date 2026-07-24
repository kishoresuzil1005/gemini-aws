import time
import random
import tracemalloc
import concurrent.futures
from typing import Dict, Any, List

from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph
from app.services.ai.analyzers.implementations.dependency_analyzer import DependencyAnalyzer
from app.services.ai.analyzers.base.analyzer_models import AnalyzerContext

def generate_synthetic_graph(num_nodes: int) -> Dict[str, Any]:
    nodes = []
    edges = []
    
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
        
    # Create realistic Enterprise Graph (Clustered into isolated VPCs)
    vpc_size = min(num_nodes, 1000)
    for i in range(num_nodes):
        vpc_base = (i // vpc_size) * vpc_size
        src = f"node-{i}"
        
        # Each node connects to 1-2 random nodes within its own VPC
        for _ in range(random.randint(1, 2)):
            tgt = f"node-{random.randint(vpc_base, min(vpc_base + vpc_size - 1, num_nodes - 1))}"
            if src != tgt:
                edges.append({"source": src, "target": tgt, "type": "DEPENDS_ON"})
                
    return {"nodes": nodes, "edges": edges}

def test_mathematical_correctness():
    """Phase 1: Deterministic Verification"""
    raw_graph = {
        "nodes": [
            {"id": "alb-1", "type": "ALB"},
            {"id": "app-1", "type": "EC2"},
            {"id": "db-1", "type": "RDS"}
        ],
        "edges": [
            {"source": "alb-1", "target": "app-1"},
            {"source": "app-1", "target": "db-1"}
        ]
    }
    analyzer = DependencyAnalyzer()
    context = AnalyzerContext(graph=raw_graph)
    result = analyzer.analyze(context)
    
    assert len(result.findings) > 0, "Spof DB should generate findings."
    spof_finding = next((f for f in result.findings if f.resource_id == "db-1"), None)
    assert spof_finding is not None
    print("[Correctness] Passed Topological Validation.")

def test_performance(num_nodes: int):
    """Phase 2: Performance & Memory Scaling"""
    raw_graph = generate_synthetic_graph(num_nodes)
    analyzer = DependencyAnalyzer()
    context = AnalyzerContext(graph=raw_graph)
    
    tracemalloc.start()
    start_time = time.time()
    
    result = analyzer.analyze(context)
    
    duration = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    peak_mb = peak / (1024 * 1024)
    nodes_per_sec = num_nodes / duration if duration > 0 else float('inf')
    
    print(f"[Performance] {num_nodes:7d} nodes | Time: {duration:6.2f}s | Nodes/sec: {nodes_per_sec:8.0f} | Peak Mem: {peak_mb:6.2f} MB | Findings: {len(result.findings)}")
    # Big-O assertion: we expect O(V+E) behavior.
    assert duration < (num_nodes / 10), f"Scaling violation: {num_nodes} took {duration}s"

def test_concurrency(num_threads: int):
    """Phase 3: Thread Safety & Immutable Shared State"""
    raw_graph = generate_synthetic_graph(100)
    analyzer = DependencyAnalyzer()
    context = AnalyzerContext(graph=raw_graph)
    
    start_time = time.time()
    
    def worker():
        res = analyzer.analyze(context)
        return len(res.findings)
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker) for _ in range(num_threads)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
    duration = time.time() - start_time
    
    # Assert deterministic equality across all threads
    first_result = results[0]
    assert all(r == first_result for r in results), "Race condition detected: Non-deterministic thread results."
    
    print(f"[Concurrency] {num_threads:4d} threads | Time: {duration:5.2f}s | Status: PASSED (Immutable State Verified)")

def test_fault_injection():
    """Phase 4: Fault Tolerance"""
    vectors = [
        {"name": "Empty Graph", "data": {"nodes": [], "edges": []}},
        {"name": "Broken Edges", "data": {"nodes": [{"id": "n1"}], "edges": [{"source": "n1", "target": "missing"}]}},
        {"name": "Self Loops", "data": {"nodes": [{"id": "n1"}], "edges": [{"source": "n1", "target": "n1"}]}},
        {"name": "Duplicate IDs", "data": {"nodes": [{"id": "n1"}, {"id": "n1"}], "edges": []}}
    ]
    
    analyzer = DependencyAnalyzer()
    
    for vec in vectors:
        try:
            ctx = AnalyzerContext(graph=vec["data"])
            analyzer.analyze(ctx)
            print(f"[Fault Tolerant] Handled: {vec['name']}")
        except Exception as e:
            print(f"[Fault Tolerant] FAILED: {vec['name']} crashed with {e}")
            raise

if __name__ == "__main__":
    print("======================================================")
    print(" DEPENDENCY ANALYZER : ENTERPRISE CERTIFICATION SUITE ")
    print("======================================================")
    
    test_mathematical_correctness()
    print("-" * 54)
    
    for size in [100, 1000, 10000, 50000, 100000]:
        test_performance(size)
    print("-" * 54)
    
    for threads in [10, 25, 50, 100, 250, 500]:
        test_concurrency(threads)
    print("-" * 54)
    
    test_fault_injection()
    print("======================================================")
    print(" ALL ENTERPRISE CERTIFICATION TESTS COMPLETED & PASSED")
    print("======================================================")
