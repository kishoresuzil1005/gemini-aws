import logging

from knowledge.service.knowledge_client import KnowledgeClient
from backend.app.services.dependency_engine.engine import DependencyIntelligenceEngine
from backend.app.services.security_engine.engine import SecurityIntelligenceEngine
from backend.app.services.cost_engine.engine import CostIntelligenceEngine
from backend.app.services.performance_engine.engine import PerformanceIntelligenceEngine
from backend.app.services.reliability_engine.engine import ReliabilityIntelligenceEngine
from backend.app.services.architecture_engine.engine import EnterpriseArchitectureIntelligenceEngine
from backend.app.services.compliance_engine.engine import EnterpriseComplianceIntelligenceEngine
from backend.app.services.governance_engine.engine import EnterpriseGovernanceIntelligenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockKnowledgeService:
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
                elif isinstance(query, str) and query.startswith("architecture:"):
                    self.data = [
                        {"id": "api-1", "resource_type": "AWS::ApiGateway::RestApi", "name": "MainAPI", "tags": {"Environment": "Prod"}}
                    ]
                else:
                    self.data = [
                        {"id": "api-1", "resource_type": "AWS::ApiGateway::RestApi", "name": "MainAPI", "tags": {"Environment": "Prod"}},
                        {"id": "ec2-1", "resource_type": "AWS::EC2::Instance", "name": "LegacyApp", "tags": {}},
                        {"id": "role-1", "resource_type": "IAM Role", "name": "AdminRole", "tags": {"BusinessOwner": "IT"}}
                    ]
        return MockResponse()

    def get_resource(self, resource_id):
        class MockResource:
            def __init__(self):
                self.resource_id = resource_id
                self.name = f"Resource-{resource_id}"
                self.resource_type = "AWS::EC2::Instance" if "ec2" in resource_id else "IAM Role" if "role" in resource_id else "AWS::ApiGateway::RestApi"
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

    # Initialize Governance Engine
    gov_engine = EnterpriseGovernanceIntelligenceEngine(
        knowledge_client=client,
        dep_engine=dep_engine,
        sec_engine=sec_engine,
        cost_engine=cost_engine,
        perf_engine=perf_engine,
        rel_engine=rel_engine,
        arch_engine=arch_engine,
        comp_engine=comp_engine
    )

    target_id = "target-prod-1"
    
    logger.info("Running Cross Engine Governance (Phase 9)...")
    assessment = gov_engine.correlate_cross_engine_data(target_id)
    
    assert assessment.ownership.status == "NON_COMPLIANT"
    assert assessment.tags.status == "NON_COMPLIANT"
    assert assessment.naming.status == "COMPLIANT"
    assert assessment.cost.unallocated_spend > 0
    assert assessment.ai_explanation != ""
    
    logger.info("Governance Assessment generated successfully.")
    
    logger.info(f"Ownership Findings: {[f.title for f in assessment.ownership.findings]}")
    logger.info(f"Tag Findings: {[f.title for f in assessment.tags.findings]}")
    logger.info(f"AI Narrative: {assessment.ai_explanation}")
    
    logger.info("Generating Implementation Report (Phase 12)...")
    report = gov_engine.generate_implementation_report()
    assert report.implementation_status == "Complete"
    logger.info("Implementation Report generated successfully.")

    print("All governance engine tests passed!")

if __name__ == "__main__":
    run_test()
