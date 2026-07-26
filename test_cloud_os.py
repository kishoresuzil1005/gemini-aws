import logging
import uuid

from knowledge.service.knowledge_client import KnowledgeClient
from app.services.cloud_os.engine import EnterpriseAICloudOS
from app.services.cloud_os.models import CloudOSRequest, CloudOSUserContext, CloudOSMultiCloudConfig

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
    logger.info("Initializing Enterprise AI Cloud Operating System...")
    
    service = MockKnowledgeService()
    client = KnowledgeClient(service)

    cloud_os = EnterpriseAICloudOS(knowledge_client=client)

    logger.info("Checking CloudOS Health...")
    health = cloud_os.check_health()
    assert health.status == "HEALTHY"
    logger.info("CloudOS is HEALTHY.")
    
    user_context = CloudOSUserContext(
        user_id="user-123",
        organization_id="org-abc",
        roles=["Admin"],
        permissions=["cloudos:execute"]
    )
    
    cloud_config = CloudOSMultiCloudConfig(
        providers=["AWS", "Azure"],
        regions=["us-east-1", "us-west-2"],
        environment="Prod"
    )

    logger.info("Testing CloudOS Dashboard Intent...")
    req_dash = CloudOSRequest(
        request_id=str(uuid.uuid4()),
        query="",
        target_id=None,
        user_context=user_context,
        cloud_config=cloud_config,
        intent="Dashboard"
    )
    resp_dash = cloud_os.process_request(req_dash)
    assert resp_dash.dashboard_data is not None
    assert "cost_summary" in resp_dash.dashboard_data
    
    logger.info("Testing CloudOS Execution Intent...")
    req_exec = CloudOSRequest(
        request_id=str(uuid.uuid4()),
        query="Resolve high CPU usage.",
        target_id="target-prod-1",
        user_context=user_context,
        cloud_config=cloud_config,
        intent="Execution"
    )
    resp_exec = cloud_os.process_request(req_exec)
    assert resp_exec.execution_plan is not None
    assert resp_exec.execution_plan.status.state == "SUCCESS"
    logger.info(f"Execution successfully processed by CloudOS.")

    logger.info("Generating Implementation Report...")
    report = cloud_os.generate_implementation_report()
    assert report.implementation_status == "Complete"
    
    print("All Enterprise AI Cloud Operating System tests passed!")

if __name__ == "__main__":
    run_test()
