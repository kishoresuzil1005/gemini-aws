from typing import List, Dict, Any
from app.models import ResourceDB

class RDSMetadata:
    """Extracts properties strictly matching the RDS metadata schema in PostgreSQL."""

    @staticmethod
    def get_vpc_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        subnet_group = metadata.get("subnet_group", {})
        if isinstance(subnet_group, dict):
            return subnet_group.get("VpcId")
        return None

    @staticmethod
    def get_security_groups(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        # Assuming flattened security groups are either 'vpc_security_groups' or 'security_groups'
        return metadata.get("vpc_security_groups") or metadata.get("security_groups", [])