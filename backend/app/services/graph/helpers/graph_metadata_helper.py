from typing import List, Any
from app.models import ResourceDB

class GraphMetadataHelper:
    """Extracts flat properties from Metadata V2."""

    @staticmethod
    def get_vpc_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("vpc_id")

    @staticmethod
    def get_subnet_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("subnet_id")

    @staticmethod
    def get_security_groups(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("security_groups", [])

    @staticmethod
    def get_ebs_volumes(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("ebs_volumes", [])

    @staticmethod
    def get_iam_profile(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("iam_instance_profile")
