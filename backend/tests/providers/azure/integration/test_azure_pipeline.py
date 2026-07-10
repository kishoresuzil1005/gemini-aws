import pytest
from unittest.mock import MagicMock, patch
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericActionRequest, GenericAction, GenericResourceType
from app.services.ai.assistant.multicloud.multicloud_engine import MultiCloudEngine
from app.providers.provider_registry import ProviderRegistry
from app.providers.azure.azure_provider import AzureProvider

@pytest.fixture
def engine():
    return MultiCloudEngine()

@pytest.fixture
def registry():
    reg = ProviderRegistry()
    # We use a mocked auth internally so it doesn't fail trying to acquire real tokens
    with patch("app.providers.azure.azure_provider.AzureAuth"):
        reg.register(CloudProvider.AZURE, lambda: AzureProvider(subscription_id="test-sub"))
    return reg

def test_azure_compute_stop_pipeline(engine, registry):
    # 1. AI issues a generic STOP COMPUTE intent
    req = GenericActionRequest(
        action=GenericAction.STOP,
        resource_type=GenericResourceType.COMPUTE,
        resource_id="/subscriptions/sub-abc-123/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-123",
        parameters={}
    )
    
    # 2. MultiCloud Engine translates this
    translated = engine.translate_request(req)
    assert translated.provider == CloudProvider.AZURE
    
    # 3. ProviderRegistry fetches the real AzureProvider
    provider = registry.get_provider(translated.provider)
    assert provider is not None
    
    # 4. Mock the compute service execute call to simulate SDK hit
    with patch.object(provider.compute, "execute", return_value={"status": "mocked SDK deallocate success"}) as mock_exec:
        # Execute action on provider
        response_dict = provider.execute_action(
            action=translated.api_call,
            resource_id=req.resource_id,
            generic_resource_type=req.resource_type,
            **translated.payload
        )
        
        # Verify provider hit SDK correctly
        mock_exec.assert_called_once_with(
            "begin_deallocate", 
            resource_group_name='rg',
            vm_name='vm-123'
        )
        
        # Verify ResponseNormalizer worked
        assert response_dict["success"] is True
        assert response_dict["data"]["status"] == "mocked SDK deallocate success"
