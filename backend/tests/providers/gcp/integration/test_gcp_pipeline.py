import pytest
from unittest.mock import MagicMock, patch
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericActionRequest, GenericAction, GenericResourceType
from app.services.ai.assistant.multicloud.multicloud_engine import MultiCloudEngine
from app.providers.provider_registry import ProviderRegistry
from app.providers.gcp.gcp_provider import GCPProvider
from google.auth.credentials import Credentials

class DummyCredentials(Credentials):
    def refresh(self, request): pass

@pytest.fixture
def engine():
    return MultiCloudEngine()

@pytest.fixture
def registry():
    reg = ProviderRegistry()
    reg.register(CloudProvider.GCP, lambda: GCPProvider())
    return reg

def test_gcp_compute_stop_pipeline(engine, registry):
    req = GenericActionRequest(
        action=GenericAction.STOP,
        resource_type=GenericResourceType.COMPUTE,
        resource_id="projects/test-project/zones/us-central1-a/instances/test-instance",
        parameters={}
    )
    
    translated = engine.translate_request(req)
    assert translated.provider == CloudProvider.GCP
    
    with patch("app.providers.gcp.gcp_provider.GCPAuth") as MockAuth:
        MockAuth.return_value.default_project_id = "test-project-id"
        MockAuth.return_value.credentials = DummyCredentials()
        provider = registry.get_provider(translated.provider)
    assert provider is not None
    
    # We expect ActionTranslator to produce api_call = "instances.stop" and payload={"instance": resource_id}
    # Then GCPTranslator shouldn't mutate it for this simple mock unless we implemented it to.
    
    with patch.object(provider.compute, "execute", return_value={"status": "mocked GCP stop success"}) as mock_exec:
        response_dict = provider.execute_action(
            action=translated.api_call,
            resource_id=req.resource_id,
            generic_resource_type=req.resource_type,
            **translated.payload
        )
        
        # Verify provider hit SDK correctly
        # Currently, ActionTranslator in Phase 7.1 outputs api_call="instances.stop" and instance=resource_id
        mock_exec.assert_called_once_with(
            "instances.stop", 
            resource_id='projects/test-project/zones/us-central1-a/instances/test-instance',
            instance='projects/test-project/zones/us-central1-a/instances/test-instance'
        )
        
        # Verify ResponseNormalizer worked
        assert response_dict["success"] is True
        assert response_dict["data"]["status"] == "mocked GCP stop success"
