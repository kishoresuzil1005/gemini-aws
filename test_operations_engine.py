import logging
import uuid

from knowledge.service.knowledge_client import KnowledgeClient
from backend.app.services.dependency_engine.engine import DependencyIntelligenceEngine
from backend.app.services.security_engine.engine import SecurityIntelligenceEngine
from backend.app.services.cost_engine.engine import CostIntelligenceEngine
from backend.app.services.performance_engine.engine import PerformanceIntelligenceEngine
from backend.app.services.reliability_engine.engine import ReliabilityIntelligenceEngine
from backend.app.services.architecture_engine.engine import EnterpriseArchitectureIntelligenceEngine
from backend.app.services.compliance_engine.engine import EnterpriseComplianceIntelligenceEngine
from backend.app.services.governance_engine.engine import EnterpriseGovernanceIntelligenceEngine
from backend.app.services.operations_engine.engine import EnterpriseOperationsIntelligenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockKnowledgeService:
    def search(self, query, *args, **kwargs):
        class MockResponse:
            def __init__(self):
                self.errors = None
                self.data = []
        return MockResponse()

    def get_resource(self, resource_id):
        class MockResource:
            def __init__(self):
                self.resource_id = resource_id
                self.name = f"Resource-{resource_id}"
                self.resource_type = "AWS::EC2::Instance"
                self.status = "AVAILABLE"
                self.configuration = {}
                self.properties = {}
        class MockResponse:
            def __init__(self):
                self.errors = None
                self.data = MockResource()
        return MockResponse()

    def get_rules(self, category=None):
        class MockResponse:
            def __init__(self):
                self.errors = None
                self.data = [{"guidance": "Test guidance"}]
        return MockResponse()

    def get_relationships(self, resource_id):
        class MockResponse:
            def __init__(self):
                self.errors = None
                self.data = []
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
    comp_engine = EnterpriseComplianceIntelligenceEngine(client, dep_engine, sec_engine, cost_engine, perf_engine, rel_engine, arch_engine)
    gov_engine = EnterpriseGovernanceIntelligenceEngine(client, dep_engine, sec_engine, cost_engine, perf_engine, rel_engine, arch_engine, comp_engine)

    # Initialize Operations Engine
    ops_engine = EnterpriseOperationsIntelligenceEngine(
        knowledge_client=client,
        dep_engine=dep_engine,
        sec_engine=sec_engine,
        cost_engine=cost_engine,
        perf_engine=perf_engine,
        rel_engine=rel_engine,
        arch_engine=arch_engine,
        comp_engine=comp_engine,
        gov_engine=gov_engine
    )

    target_id = "target-prod-1"
    
    logger.info("Running Cross Engine Operations (Phase 9)...")
    assessment = ops_engine.correlate_cross_engine_data(target_id)
    
    assert assessment.health_profile is not None
    assert assessment.incident_assessment is not None
    assert assessment.change_impact is not None
    assert assessment.ai_explanation != ""
    assert assessment.dashboard is not None
    
    logger.info("Operations Assessment generated successfully.")
    
    logger.info(f"Health Status: {assessment.health_profile.health.status}")
    logger.info(f"Active Incidents: {len(assessment.incident_assessment.active_incidents)}")
    logger.info(f"AI Narrative: {assessment.ai_explanation}")
    
    logger.info("Generating Implementation Report (Phase 12)...")
    report = ops_engine.generate_implementation_report()
    assert report.implementation_status == "Complete"
    logger.info("Implementation Report generated successfully.")

    print("All operations engine tests passed!")

if __name__ == "__main__":
    run_test()
