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
from app.services.recommendation_engine.engine import EnterpriseAIRecommendationEngine
from app.services.recommendation_engine.models import RecommendationRequest, RecommendationContext

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

    target_id = "target-prod-1"
    
    logger.info("Running Recommendation Engine Test...")
    
    req = RecommendationRequest(
        request_id=str(uuid.uuid4()),
        target_id=target_id,
        query="Why is there a 502 Bad Gateway?",
        context=RecommendationContext(
            target_id=target_id,
            objectives=["Restore Service", "Minimize Cost"],
            constraints=["No manual downtime allowed"]
        )
    )
    
    recs = rec_engine.generate_recommendations(req)
    
    assert len(recs) >= 2 # Best and Alternative
    best_rec = next((r for r in recs if r.status == "BEST"), None)
    assert best_rec is not None
    assert len(best_rec.tradeoffs.advantages) > 0
    assert best_rec.plan.estimated_duration != ""
    assert best_rec.explanation != ""
    
    logger.info("Recommendation Engine generated recommendations successfully.")
    logger.info(f"Executive Recommendation: {rec_engine.generate_decision_support(recs).executive_recommendation}")
    
    logger.info("Testing Recommendation Comparison...")
    comp = rec_engine.compare_options(recs[0], recs[1], "Scale Up vs Scale Out")
    assert comp.winner != ""
    logger.info("Recommendation Comparison generated successfully.")

    logger.info("Testing Multi-Objective Optimization...")
    opt_set = rec_engine.optimize(req, recs)
    assert opt_set.overall_score > 0
    logger.info("Multi-Objective Optimization completed.")

    logger.info("Generating Implementation Report...")
    report = rec_engine.generate_implementation_report()
    assert report.implementation_status == "Complete"
    logger.info("Implementation Report generated successfully.")

    print("All Recommendation Engine tests passed!")

if __name__ == "__main__":
    run_test()
