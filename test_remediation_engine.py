import logging
import uuid

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
from app.services.recommendation_engine.engine import EnterpriseAIRecommendationEngine
from app.services.remediation_engine.engine import EnterpriseAIRemediationEngine
from app.services.remediation_engine.models import RemediationRequest

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
    logger.info("Initializing Stack...")
    
    service = MockKnowledgeService()
    client = KnowledgeClient(service)

    dep_engine = DependencyIntelligenceEngine(client)
    sec_engine = SecurityIntelligenceEngine(client, dep_engine)
    cost_engine = CostIntelligenceEngine(client, dep_engine, sec_engine)
    perf_engine = PerformanceIntelligenceEngine(client, dep_engine, sec_engine, cost_engine)
    rel_engine = ReliabilityIntelligenceEngine(client, dep_engine, sec_engine, cost_engine, perf_engine)
    arch_engine = EnterpriseArchitectureIntelligenceEngine(client, dep_engine, sec_engine, cost_engine, perf_engine, rel_engine)
    comp_engine = EnterpriseComplianceIntelligenceEngine(client, dep_engine, sec_engine, cost_engine, perf_engine, rel_engine, arch_engine)
    gov_engine = EnterpriseGovernanceIntelligenceEngine(client, dep_engine, sec_engine, cost_engine, perf_engine, rel_engine, arch_engine, comp_engine)
    ops_engine = EnterpriseOperationsIntelligenceEngine(client, dep_engine, sec_engine, cost_engine, perf_engine, rel_engine, arch_engine, comp_engine, gov_engine)

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

    rec_engine = EnterpriseAIRecommendationEngine(ai_orchestrator)
    rem_engine = EnterpriseAIRemediationEngine(rec_engine)

    target_id = "target-prod-1"
    
    logger.info("Running Remediation Engine Test...")
    
    req = RemediationRequest(
        request_id=str(uuid.uuid4()),
        target_id=target_id,
        query="Fix the 502 Bad Gateway issue on this resource."
    )
    
    plan = rem_engine.generate_plan(req)
    
    assert plan is not None
    assert plan.target_id == target_id
    assert len(plan.rollback_plan.rollback_order) > 0
    assert len(plan.validation_plan.post_validation) > 0
    assert plan.approval_requirement.approval_required is True
    assert plan.execution_readiness.ready_for_execution is True
    
    logger.info(f"Remediation Plan Generated: {plan.summary.executive_plan}")
    
    logger.info("Generating Implementation Report...")
    report = rem_engine.generate_implementation_report()
    assert report.implementation_status == "Complete"
    
    print("All Remediation Engine tests passed!")

if __name__ == "__main__":
    run_test()
