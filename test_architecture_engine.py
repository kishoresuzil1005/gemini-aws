import asyncio
import logging
import sys

from knowledge.service.knowledge_client import KnowledgeClient
from backend.app.services.dependency_engine.engine import DependencyIntelligenceEngine
from backend.app.services.security_engine.engine import SecurityIntelligenceEngine
from backend.app.services.cost_engine.engine import CostIntelligenceEngine
from backend.app.services.performance_engine.engine import PerformanceIntelligenceEngine
from backend.app.services.reliability_engine.engine import ReliabilityIntelligenceEngine
from backend.app.services.architecture_engine.engine import EnterpriseArchitectureIntelligenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockKnowledgeService:
    def get_resource(self, resource_id):
        class MockResource:
            def __init__(self):
                self.resource_id = resource_id
                self.name = f"Resource-{resource_id}"
                self.resource_type = "AWS::EC2::Instance" if "ec2" in resource_id else "AWS::RDS::DBInstance"
                self.status = "AVAILABLE"
                self.configuration = {}
                
        class MockResponse:
            def __init__(self):
                self.errors = None
                self.data = MockResource()
        return MockResponse()

    def search(self, query, *args, **kwargs):
        class MockResponse:
            def __init__(self):
                self.errors = None
                if isinstance(query, str) and query.startswith("relationships:"):
                    class MockRelationship:
                        def __init__(self):
                            self.source_id = query.split(":")[1]
                            self.target_id = "target-1"
                            self.type = "depends_on"
                            self.metadata = {}
                    self.data = [MockRelationship()]
                else:
                    self.data = [
                        {"id": "api-1", "resource_type": "AWS::ApiGateway::RestApi", "name": "MainAPI"},
                        {"id": "lambda-1", "resource_type": "AWS::Lambda::Function", "name": "Processor"},
                        {"id": "db-1", "resource_type": "AWS::RDS::DBInstance", "name": "PrimaryDB"},
                        {"id": "ec2-1", "resource_type": "AWS::EC2::Instance", "name": "LegacyApp"},
                        {"id": "sqs-1", "resource_type": "AWS::SQS::Queue", "name": "JobQueue"},
                        {"id": "alb-1", "resource_type": "AWS::ElasticLoadBalancingV2::LoadBalancer", "name": "MainALB"}
                    ]
        return MockResponse()

    def get_relationships(self, resource_id):
        class MockRelationship:
            def __init__(self):
                self.source_id = resource_id
                self.target_id = "target-1"
                self.type = "depends_on"
                self.metadata = {}
        class MockResponse:
            def __init__(self):
                self.errors = None
                self.data = [MockRelationship()]
        return MockResponse()

def run_test():
    logger.info("Initializing Intelligence Engines...")
    
    # Initialize the mocked Knowledge Service
    service = MockKnowledgeService()
    client = KnowledgeClient(service)

    # Initialize frozen engines
    dep_engine = DependencyIntelligenceEngine(client)
    sec_engine = SecurityIntelligenceEngine(client, dep_engine)
    cost_engine = CostIntelligenceEngine(client, dep_engine, sec_engine)
    perf_engine = PerformanceIntelligenceEngine(client, dep_engine, sec_engine, cost_engine)
    rel_engine = ReliabilityIntelligenceEngine(client, dep_engine, sec_engine, cost_engine, perf_engine)

    # Initialize Architecture Engine
    arch_engine = EnterpriseArchitectureIntelligenceEngine(
        knowledge_client=client,
        dep_engine=dep_engine,
        sec_engine=sec_engine,
        cost_engine=cost_engine,
        perf_engine=perf_engine,
        rel_engine=rel_engine
    )

    architecture_id = "arch-prod-1"
    
    logger.info("Running Cross Engine Validation (Phase 11)...")
    assessment = arch_engine.cross_engine_validation(architecture_id)
    
    assert assessment.topology is not None
    assert len(assessment.topology.api_gateways) > 0
    assert assessment.patterns is not None
    assert assessment.anti_patterns is not None
    assert assessment.well_architected is not None
    assert assessment.scalability is not None
    assert assessment.modernization is not None
    assert assessment.tradeoffs is not None
    assert assessment.decision is not None
    assert assessment.ai_explanation != ""
    
    logger.info("Architecture Assessment generated successfully.")
    
    logger.info(f"Detected Patterns: {[p.name for p in assessment.patterns]}")
    logger.info(f"Detected Anti-Patterns: {[ap.name for ap in assessment.anti_patterns]}")
    logger.info(f"AI Narrative: {assessment.architecture_narrative}")
    
    logger.info("Generating Implementation Report (Phase 12)...")
    report = arch_engine.generate_implementation_report()
    assert report.implementation_status == "Complete"
    logger.info("Implementation Report generated successfully.")

    print("All architecture engine tests passed!")

if __name__ == "__main__":
    run_test()
