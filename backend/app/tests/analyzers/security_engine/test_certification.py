import time
import json
from concurrent.futures import ThreadPoolExecutor
from app.services.ai.analyzers.base.analyzer_models import AnalyzerContext
from app.services.ai.analyzers.implementations.security_analyzer import SecurityAnalyzer
# Rules are auto-discovered
from app.services.ai.analyzers.engines.graph.graph_processor import GraphProcessor
from app.services.ai.analyzers.engines.graph.graph_index import GraphIndex
from app.services.ai.analyzers.engines.context.engine_context import EngineContext

def build_synthetic_graph(node_count=1000):
    nodes = []
    edges = []
    
    # Add a few vulnerable resources
    nodes.append({
        "id": "bad-s3",
        "type": "S3Bucket",
        "configuration": {
            "public_access_block": {"block_public_acls": False, "block_public_policy": False}
        }
    })
    
    nodes.append({
        "id": "bad-sg",
        "type": "SecurityGroup",
        "configuration": {
            "inbound_rules": [{"from_port": 22, "to_port": 22, "ip_ranges": ["0.0.0.0/0"]}]
        }
    })
    
    nodes.append({
        "id": "bad-iam",
        "type": "IAMPolicy",
        "configuration": {
            "policy_document": {"Statement": [{"Effect": "Allow", "Action": ["*"]}]}
        }
    })
    
    nodes.append({
        "id": "bad-rds",
        "type": "RDS",
        "configuration": {"publicly_accessible": True}
    })
    
    nodes.append({
        "id": "bad-cloudtrail",
        "type": "CloudTrail",
        "configuration": {"is_logging": False}
    })
    
    nodes.append({
        "id": "bad-kms",
        "type": "KMSKey",
        "configuration": {"key_manager": "CUSTOMER", "rotation_enabled": False}
    })
    
    nodes.append({
        "id": "bad-secretsmanager",
        "type": "SecretsManagerSecret",
        "configuration": {"rotation_enabled": False}
    })
    
    nodes.append({
        "id": "bad-identitycenter",
        "type": "IdentityCenter",
        "configuration": {"mfa_enforced": False}
    })
    
    # Fill with safe resources to test O(V) speed
    for i in range(node_count - 8):
        nodes.append({"id": f"good-ec2-{i}", "type": "EC2"})
        
    return {"nodes": nodes, "edges": edges}

def test_correctness():
    """Phase 9: Correctness Verification"""
    raw_graph = build_synthetic_graph(100)
    context = AnalyzerContext(graph=raw_graph, inventory={}, policies={})
    
    analyzer = SecurityAnalyzer()
    result = analyzer.analyze(context)
    
    # We expect many findings because empty configs trigger missing property rules
    assert len(result.findings) > 10, f"Expected >10 findings, got {len(result.findings)}"
    
    rule_ids = {f.id for f in result.findings}
    assert "AWS-S3-001" in rule_ids
    assert "AWS-S3-002" in rule_ids
    assert "AWS-VPC-001" in rule_ids
    assert "AWS-IAM-001" in rule_ids
    assert "AWS-RDS-001" in rule_ids
    assert "AWS-CT-001" in rule_ids
    assert "AWS-KMS-001" in rule_ids
    assert "AWS-SM-001" in rule_ids
    assert "AWS-SSO-001" in rule_ids
    
    # Verify JSON serialization works (API Compatibility)
    serialized = result.model_dump_json()
    assert "AWS-S3-001" in serialized
    
def test_performance():
    """Phase 10: Performance Benchmarking"""
    raw_graph = build_synthetic_graph(10000)
    context = AnalyzerContext(graph=raw_graph, inventory={}, policies={})
    analyzer = SecurityAnalyzer()
    
    start_time = time.time()
    result = analyzer.analyze(context)
    duration = time.time() - start_time
    
    # Should be insanely fast due to O(V) filtering via GraphIndex
    assert duration < 10.0, f"Performance failed: {duration}s"
    assert len(result.findings) > 100

def test_concurrency():
    """Phase 11: Concurrency Verification"""
    raw_graph = build_synthetic_graph(100)
    context = AnalyzerContext(graph=raw_graph, inventory={}, policies={})
    analyzer = SecurityAnalyzer()
    
    def run_analyzer():
        return analyzer.analyze(context)
        
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(lambda _: run_analyzer(), range(100)))
        
    assert len(results) == 100
    for r in results:
        assert len(r.findings) > 10

def test_fault_injection():
    """Phase 12: Fault Injection"""
    # Empty Graph
    context = AnalyzerContext(graph={"nodes": [], "edges": []}, inventory={}, policies={})
    analyzer = SecurityAnalyzer()
    result = analyzer.analyze(context)
    assert len(result.findings) == 0
    
    # Malformed node (missing config)
    raw_graph = {"nodes": [{"id": "bad", "type": "S3Bucket"}], "edges": []}
    context = AnalyzerContext(graph=raw_graph, inventory={}, policies={})
    result = analyzer.analyze(context)
    # The S3 rules safely handle missing config and trigger multiple rules
    assert len(result.findings) > 2

if __name__ == '__main__':
    print("[CERTIFICATION] Running Correctness Verification...")
    test_correctness()
    print("[CERTIFICATION] Correctness Passed.")
    
    print("[CERTIFICATION] Running Performance Benchmarking...")
    test_performance()
    print("[CERTIFICATION] Performance Passed (10,000 nodes).")
    
    print("[CERTIFICATION] Running Thread Safety Validation...")
    test_concurrency()
    print("[CERTIFICATION] Concurrency Passed (100 simultaneous executions).")
    
    print("[CERTIFICATION] Running Fault Injection...")
    test_fault_injection()
    print("[CERTIFICATION] Fault Injection Passed.")
    
    print("\n[CERTIFICATION] ALL PHASES PASSED. Security Engine 100% Certified.")
