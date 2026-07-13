from typing import List
from app.models import ResourceDB

class EC2Metadata:
    """Extracts properties strictly matching the EC2 metadata schema in PostgreSQL."""

    @staticmethod
    def get_vpc_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("vpc_id")

    @staticmethod
    def get_subnet_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("subnet_id")

    @staticmethod
    def get_ebs_volumes(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("ebs_volumes", [])

    @staticmethod
    def get_security_groups(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("security_groups", [])

    @staticmethod
    def get_iam_instance_profile(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("iam_instance_profile"