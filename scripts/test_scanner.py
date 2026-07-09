import os
import sys

# Setup mock environment for boto3 if needed, but since we just want to run the scanner we can import it.
# Actually, the EC2 provider will fail if boto3 is not configured, but it catches exceptions and logs them.
# I can mock boto3 so we get dummy data, or I can just let it run.
# Let's mock boto3 so we can test the pipeline without AWS creds.

from unittest.mock import patch, MagicMock

# Create mock for boto3.client
boto3_mock = MagicMock()
ec2_client = MagicMock()
boto3_mock.client.return_value = ec2_client

paginator = MagicMock()
ec2_client.get_paginator.return_value = paginator
paginator.paginate.return_value = [{
    "Reservations": [{
        "Instances": [{
            "InstanceId": "i-1234567890abcdef0",
            "State": {"Name": "running"},
            "InstanceType": "t3.micro",
            "LaunchTime": "2023-01-01T00:00:00Z",
            "VpcId": "vpc-0abc123",
            "SubnetId": "subnet-0abc123",
            "SecurityGroups": [{"GroupId": "sg-0abc123"}]
        }]
    }]
}]

with patch('boto3.client', boto3_mock):
    sys.path.insert(0, os.path.abspath('backend'))
    from app.services.discovery.scanner import AWSDiscoveryScanner
    from app.services.discovery.normalizer import ResourceNormalizer

    scan_result = AWSDiscoveryScanner.scan_all(region="us-east-1")
    if scan_result.resources:
        print("--- RAW RESOURCES [0] ---")
        print(scan_result.resources[0])
        
        normalized = ResourceNormalizer.normalize(scan_result.resources)
        print("\n--- NORMALIZED RESOURCES [0] ---")
        print(normalized[0])
    else:
        print("No resources found.")
