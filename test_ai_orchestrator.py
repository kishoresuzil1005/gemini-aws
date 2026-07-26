import logging
import uuid
import datetime

from knowledge.service.knowledge_client import KnowledgeClient
from app.services.dependency_engine.engine import DependencyIntelligenceEngine
from app.services.security_engine.engine import SecurityIntelligenceEngine
from app.services.cost_engine.engine import CostIntelligenceEngine
from app.services.performance_engine.engine import PerformanceIntelligenceEngine
from app.services.reliability_engine.engine import ReliabilityIntelligenceEngine
from app.services.architecture_engine.engine import EnterpriseArchitectureIntelligenceEngine
from app.services.compliance_engine.engine import EnterpriseComplianceIntelligenceEngine
from app.services.governance_engine.engine import EnterpriseGovernanceIntelligenceEngine
from app.services.operations_engine.engine import EnterpriseOperationsIntelligenceEngine
from app.services.ai_orchestrator.engine import EnterpriseAIReasoningOrchestrator
from app.services.ai_orchestrator.models import AIRequest

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

    def search_resources(self, query):
         return [{"id": "api-1", "resource_type": "AWS::ApiGateway::RestApi", "name": "MainAPI", "tags": {"Environment": "Prod"}}]

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
    ops_engine = EnterpriseOperationsIntelligenceEngine(client, dep_engine, sec_engine, cost_engine, perf_engine, rel_engine, arch_engine, comp_engine, gov_engine)

    # Initialize AI Orchestrator
    ai_orchestrator = EnterpriseAIReasoningOrchestrator(
        knowledge_client=client,
        dep_engine=dep_engine,
        sec_engine=sec_engine,
        cost_engine=cost_engine,
        perf_engine=perf_engine,
        rel_engine=rel_engine,
        arch_engine=arch_engine,
        comp_engine=comp_engine,
        gov_engine=gov_engine,
        ops_engine=ops_engine
    )

    target_id = "target-prod-1"
    
    logger.info("Running AI Orchestrator Test...")
    
    # Test Scenario 1: Incident
    req1 = AIRequest(
        id=str(uuid.uuid4()),
        target_id=target_id,
        query="Why is there a 502 Bad Gateway?"
    )
    
    response1 = ai_orchestrator.generate_response(req1)
    
    assert response1.executive_summary.status == "CRITICAL"
    assert "Dependency" in response1.reasoning_chain.plan.execution_order
    assert len(response1.reasoning_chain.evidence) > 0
    assert len(response1.recommended_actions) > 0
    assert response1.unified_explanation != ""
    
    logger.info("AI Orchestrator processed Incident request successfully.")
    logger.info(f"Unified Explanation:\n{response1.unified_explanation}")
    
    # Test Scenario 2: Architecture Review
    req2 = AIRequest(
        id=str(uuid.uuid4()),
        target_id=target_id,
        query="Perform an architecture review for this workload."
    )
    
    response2 = ai_orchestrator.generate_response(req2)
    assert response2.executive_summary.status == "STABLE"
    assert "Architecture" in response2.reasoning_chain.plan.execution_order
    logger.info("AI Orchestrator processed Architecture Review request successfully.")

    logger.info("Generating Implementation Report...")
    report = ai_orchestrator.generate_implementation_report()
    assert report.implementation_status == "Complete"
    logger.info("Implementation Report generated successfully.")

    print("All AI Orchestrator tests passed!")

if __name__ == "__main__":
    run_test()
