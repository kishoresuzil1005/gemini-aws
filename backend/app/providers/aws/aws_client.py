import boto3
from typing import Optional

class AWSClientManager:
    """
    Centralized manager for Boto3 sessions to ensure we reuse connections
    and handle cross-account assume-role if necessary.
    """
    def __init__(self, region_name: str = "us-east-1", profile_name: Optional[str] = None):
        self.region_name = region_name
        self.profile_name = profile_name
        self._session = boto3.Session(region_name=self.region_name, profile_name=self.profile_name)

    def get_client(self, service_name: str):
        return self._session.client(service_name)
    
    def get_resource(self, service_name: str):
        return self._session.resource(service_name)
