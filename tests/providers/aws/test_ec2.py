import pytest
from unittest.mock import MagicMock
from app.providers.aws.ec2_service import EC2Service
from app.providers.aws.aws_client import AWSClientManager

def test_describe_instances():
    # Setup mock
    mock_client_manager = MagicMock(spec=AWSClientManager)
    mock_boto_client = MagicMock()
    mock_client_manager.get_client.return_value = mock_boto_client
    
    mock_boto_client.describe_instances.return_value = {
        "Reservations": [
            {"Instances": [{"InstanceId": "i-1234567890abcdef0"}]}
        ]
    }
    
    # Test service
    ec2_service = EC2Service(mock_client_manager)
    instances = ec2_service.describe_instances()
    
    # Assertions
    assert len(instances) == 1
    assert instances[0]["InstanceId"] == "i-1234567890abcdef0"
    mock_boto_client.describe_instances.assert_called_once()
