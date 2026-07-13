from typing import List, Dict, Any
from app.models import ResourceDB

class LambdaMetadata:
    """Extracts properties strictly matching the Lambda flat metadata schema in PostgreSQL."""

    @staticmethod
    def get_role(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("role")

    @staticmethod
    def get_vpc_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        vpc_config = metadata.get("vpc_config", {})
        if isinstance(vpc_config, dict):
            return vpc_config.get("VpcId") or vpc_config.get("vpc_id")
        return None

    @staticmethod
    def get_subnet_ids(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        vpc_config = metadata.get("vpc_config", {})
        if isinstance(vpc_config, dict):
            return vpc_config.get("SubnetIds", [])
        return []

    @staticmethod
    def get_security_group_ids(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        vpc_config = metadata.get("vpc_config", {})
        if isinstance(vpc_config, dict):
            return vpc_config.get("SecurityGroupIds", [])
        return []