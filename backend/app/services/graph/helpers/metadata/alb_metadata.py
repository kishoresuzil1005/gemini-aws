from typing import List, Dict, Any
from app.models import ResourceDB

class ALBMetadata:
    """Extracts properties strictly matching the flat ALB / TargetGroup schema in PostgreSQL."""

    @staticmethod
    def get_vpc_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("vpc_id")

    @staticmethod
    def get_subnet_ids(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("subnets", [])

    @staticmethod
    def get_security_groups(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("security_groups", [])

    @staticmethod
    def get_load_balancers(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("load_balancers", [])

    @staticmethod
    def get_targets(resource: ResourceDB) -> List[Dict[str, Any]]:
        metadata = resource.resource_metadata or {}
        return metadata.get("targets", [])