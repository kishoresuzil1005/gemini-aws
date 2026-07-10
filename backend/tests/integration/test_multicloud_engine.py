import pytest
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericActionRequest, GenericAction, GenericResourceType
from app.services.ai.assistant.multicloud.multicloud_engine import MultiCloudEngine
from app.services.ai.assistant.multicloud.provider_selector import ProviderNotFoundError
from app.services.ai.assistant.multicloud.resource_mapper import UnsupportedResourceError
from app.services.ai.assistant.multicloud.provider_capability import UnsupportedCapabilityError

@pytest.fixture
def engine():
    return MultiCloudEngine()

def test_stop_compute_aws(engine):
    req = GenericActionRequest(
        action=GenericAction.STOP,
        resource_type=GenericResourceType.COMPUTE,
        resource_id="arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0",
        parameters={}
    )
    payload = engine.translate_request(req)
    
    assert payload.provider == CloudProvider.AWS
    assert payload.api_call == "stop_instances"
    assert "InstanceIds" in payload.payload
    assert payload.payload["InstanceIds"] == [req.resource_id]

def test_stop_compute_azure(engine):
    req = GenericActionRequest(
        action=GenericAction.STOP,
        resource_type=GenericResourceType.COMPUTE,
        resource_id="/subscriptions/sub-abc-123/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-123",
        parameters={}
    )
    payload = engine.translate_request(req)
    
    assert payload.provider == CloudProvider.AZURE
    assert payload.api_call == "begin_deallocate"
    assert payload.payload["vm_name"] == req.resource_id

def test_stop_compute_gcp(engine):
    req = GenericActionRequest(
        action=GenericAction.STOP,
        resource_type=GenericResourceType.COMPUTE,
        resource_id="projects/project-xyz-456/zones/us-central1-a/instances/inst-123",
        parameters={}
    )
    payload = engine.translate_request(req)
    
    assert payload.provider == CloudProvider.GCP
    assert payload.api_call == "instances.stop"
    assert payload.payload["instance"] == req.resource_id

def test_delete_database_aws_unsupported(engine):
    req = GenericActionRequest(
        action=GenericAction.DELETE,
        resource_type=GenericResourceType.DATABASE,
        resource_id="arn:aws:rds:us-east-1:123456789012:db:mydb",
        parameters={}
    )
    with pytest.raises(UnsupportedCapabilityError):
        engine.translate_request(req)

def test_unknown_provider(engine):
    req = GenericActionRequest(
        action=GenericAction.STOP,
        resource_type=GenericResourceType.COMPUTE,
        resource_id="unknown-resource-id-with-no-clues",
        parameters={}
    )
    with pytest.raises(ProviderNotFoundError):
        # We enforce an unconnected provider override
        engine.translate_request(req, explicit_provider=CloudProvider.OCI)

def test_unknown_resource(engine):
    req = GenericActionRequest(
        action=GenericAction.STOP,
        resource_type=GenericResourceType.IDENTITY, # Mapped but unsupported generic resource type in mock
        resource_id="arn:aws:iam::123456789012:user/Bob",
        parameters={}
    )
    with pytest.raises(UnsupportedResourceError):
        # IDENTITY is in GenericResourceType but not present in ResourceMapper's MAPPING dict
        engine.translate_request(req)
