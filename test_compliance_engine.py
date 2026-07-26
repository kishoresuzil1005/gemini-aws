import logging

from knowledge.service.knowledge_client import KnowledgeClient
from backend.app.services.dependency_engine.engine import DependencyIntelligenceEngine
from backend.app.services.security_engine.engine import SecurityIntelligenceEngine
from backend.app.services.cost_engine.engine import CostIntelligenceEngine
from backend.app.services.performance_engine.engine import PerformanceIntelligenceEngine
from backend.app.services.reliability_engine.engine import ReliabilityIntelligenceEngine
from backend.app.services.architecture_engine.engine import EnterpriseArchitectureIntelligenceEngine
from backend.app.services.compliance_engine.engine import EnterpriseComplianceIntelligenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockKnowledgeService:
    def get_resource(self, resource_id):
        class MockResource:
            def __init__(self):
                self.resource_id = resource_id
                self.name = f"Resource-{resource_id}"
                self.resource_type = "AWS::EC2::Instance"
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
                        {"id": "api-1", "resource_type": "AWS::ApiGateway::RestApi", "name": "MainAPI"}
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

    def get_rules(self, category=None):
        class MockResponse:
            def __init__(self):
                self.errors = None
                self.data = [{"guidance": "Test guidance"}]
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
    arch_engine = EnterpriseArchitectureIntelligenceEngine(client, dep_engine, sec_engine, cost_engine, perf_engine, rel_engine)

    # Initialize Compliance Engine
    comp_engine = EnterpriseComplianceIntelligenceEngine(
        knowledge_client=client,
        dep_engine=dep_engine,
        sec_engine=sec_engine,
        cost_engine=cost_engine,
        perf_engine=perf_engine,
        rel_engine=rel_engine,
        arch_engine=arch_engine
    )

    target_id = "target-prod-1"
    
    logger.info("Running Cross Engine Reasoning (Phase 8 & 9)...")
    assessment = comp_engine.correlate_cross_engine_data(target_id)
    
    assert assessment.score is not None
    assert assessment.risk is not None
    assert assessment.gaps is not None
    assert len(assessment.frameworks) > 0
    assert assessment.ai_explanation != ""
    
    logger.info("Compliance Assessment generated successfully.")
    
    logger.info(f"Identified Gaps: {[g.gap_type for g in assessment.gaps]}")
    logger.info(f"AI Narrative: {assessment.ai_explanation}")
    
    logger.info("Generating Implementation Report (Phase 10)...")
    report = comp_engine.generate_implementation_report()
    assert report.implementation_status == "Complete"
    logger.info("Implementation Report generated successfully.")

    print("All compliance engine tests passed!")

if __name__ == "__main__":
    run_test()
