import pytest
from app.services.ai.assistant.knowledge_graph.core.graph_engine import GraphEngine
from app.services.ai.assistant.knowledge_graph.core.graph_repository import GraphRepository
from app.services.ai.assistant.knowledge_graph.builders.aws_builder import AWSGraphBuilder
from app.services.ai.assistant.knowledge_graph.builders.kubernetes_builder import KubernetesGraphBuilder
from app.services.ai.assistant.knowledge_graph.builders.graph_builder import GraphBuilderCoordinator
from app.services.ai.assistant.knowledge_graph.query.graph_traversal import GraphTraversal
from app.services.ai.assistant.knowledge_graph.intelligence.blast_radius_engine import BlastRadiusEngine
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider

def test_multicloud_blast_radius():
    engine = GraphEngine()
    repository = GraphRepository(engine)
    
    coordinator = GraphBuilderCoordinator()
    coordinator.register_builder(CloudProvider.AWS, AWSGraphBuilder())
    coordinator.register_builder(CloudProvider.KUBERNETES, KubernetesGraphBuilder())
    
    # 1. Build Nodes
    nodes = coordinator.build_all_nodes()
    for node in nodes:
        repository.save_node(node)
        
    # 2. Build Edges
    edges = coordinator.build_all_edges()
    for edge in edges:
        repository.save_edge(edge)
        
    # 3. Add a synthetic Cross-Cloud Edge (Simulating the GraphMerger)
    from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudEdge
    cross_edge = CloudEdge(
        source_id="arn:aws:ec2:us-east-1:123456789012:instance/i-0abcdef1234567890",
        target_id="namespaces/default/deployments/payment-service",
        relationship_type="HOSTS"
    )
    repository.save_edge(cross_edge)
    
    # 4. Traversal & Blast Radius
    traversal = GraphTraversal(repository)
    blast_engine = BlastRadiusEngine(traversal)
    
    # Target the AWS EC2 instance
    result = blast_engine.calculate_impact("arn:aws:ec2:us-east-1:123456789012:instance/i-0abcdef1234567890")
    
    # It should hit the IAM role (from aws_builder), itself, the K8s deployment (cross_edge), 
    # and the K8s pod (from kubernetes_builder). Total = 4
    assert result["affected_count"] == 4
    assert "namespaces/default/pods/payment-service-pod-1" in result["affected_nodes"]
    assert "arn:aws:iam::123456789012:role/DemoRole" in result["affected_nodes"]
