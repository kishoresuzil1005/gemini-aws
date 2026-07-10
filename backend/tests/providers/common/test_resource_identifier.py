import pytest
from app.providers.common.resource_identifier import GenericResourceIdentifier

def test_parse_aws_arn():
    arn = "arn:aws:ec2:us-east-1:123456789012:instance/i-0abcdef1234567890"
    res = GenericResourceIdentifier.parse_aws_arn(arn)
    assert res.provider == "AWS"
    assert res.resource_type == "instance"
    assert res.resource_name == "i-0abcdef1234567890"
    assert res.region == "us-east-1"
    assert res.account_id == "123456789012"
    assert res.unique_id == arn

def test_parse_azure_id():
    azure_id = "/subscriptions/sub-123/resourceGroups/rg-1/providers/Microsoft.Compute/virtualMachines/vm-1"
    res = GenericResourceIdentifier.parse_azure_id(azure_id)
    assert res.provider == "AZURE"
    assert res.resource_type == "virtualMachines"
    assert res.resource_name == "vm-1"
    assert res.subscription == "sub-123"

def test_parse_gcp_uri():
    gcp_uri = "projects/my-proj/zones/us-central1-a/instances/vm1"
    res = GenericResourceIdentifier.parse_gcp_uri(gcp_uri)
    assert res.provider == "GCP"
    assert res.resource_type == "instances"
    assert res.resource_name == "vm1"
    assert res.project == "my-proj"
    assert res.zone == "us-central1-a"

def test_parse_kubernetes_uri():
    k8s_uri = "namespaces/kube-system/pods/coredns-123"
    res = GenericResourceIdentifier.parse_kubernetes_uri(k8s_uri)
    assert res.provider == "KUBERNETES"
    assert res.resource_type == "pods"
    assert res.resource_name == "coredns-123"
    assert res.namespace == "kube-system"
