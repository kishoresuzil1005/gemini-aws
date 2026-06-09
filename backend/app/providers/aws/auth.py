import boto3
from app.config import settings

def get_aws_client(service, region="us-east-1"):
    # Future: Implement STS AssumeRole logic
    return boto3.client(service, region_name=region)
