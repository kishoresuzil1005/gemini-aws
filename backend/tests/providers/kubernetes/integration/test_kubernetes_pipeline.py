import pytest
from unittest.mock import patch, MagicMock
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericActionRequest, GenericAction, GenericResourceType
from app.services.ai.assistant.multicloud.multicloud_engine import MultiCloudEngine
from app.providers.provider_registry import ProviderRegistry
from app.providers.kubernetes.kubernetes_provider import KubernetesProvider

@pytest.fixture
def engine():
    return MultiCloudEngine()

@pytest.fixture
def registry():
    reg = ProviderRegistry()
    reg.register(CloudProvider.KUBERNETES, lambda: KubernetesProvider())
    return reg

def test_kubernetes_deployment_stop_pipeline(engine, registry):
    req = GenericActionRequest(
        action=GenericAction.STOP,
        resource_type=GenericResourceType.COMPUTE,
        resource_id="namespaces/default/deployments/payment-service",
        parameters={}
    )
    
    # We patch the translator payload generator in MultiCloudEngine to explicitly route to kubernetes
    with patch.object(engine, "translate_request") as mock_translate:
        from app.services.ai.assistant.multicloud.multicloud_models import TranslatedActionPayload
        mock_translate.return_value = TranslatedActionPayload(
            provider=CloudProvider.KUBERNETES,
            api_call="STOP",
            payload={}
        )
        translated = engine.translate_request(req)
        
    assert translated.provider == CloudProvider.KUBERNETES
    
    with patch("app.providers.kubernetes.kubernetes_provider.KubernetesAuth"):
        provider = registry.get_provider(translated.provider)
        
    assert provider is not None
    
    with patch.object(provider.deployment.api, "patch_namespaced_deployment_scale", return_value={"status": "mocked k8s patch success"}) as mock_exec:
        response_dict = provider.execute_action(
            action=translated.api_call,
            resource_id=req.resource_id,
            generic_resource_type=req.resource_type,
            **translated.payload
        )
        
        # Verify provider hit SDK correctly (scaled to 0)
        mock_exec.assert_called_once_with(
            name='payment-service',
            namespace='default',
            body={'spec': {'replicas': 0}}
        )
        
        # Verify ResponseNormalizer worked
        assert response_dict["success"] is True
        assert response_dict["data"]["status"] == "mocked k8s patch success"
