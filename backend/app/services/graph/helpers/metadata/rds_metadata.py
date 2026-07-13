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

        groups = metadata.get("vpc_security_groups", [])

        if groups and isinstance(groups[0], dict):
            return [
                sg.get("VpcSecurityGroupId")
                for sg in groups
                if sg.get("VpcSecurityGroupId")
            ]

        return groups

    @staticmethod
    def get_subnets(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}

        subnet_group = metadata.get("subnet_group", {})

        subnets = subnet_group.get("Subnets", [])

        return [
            subnet.get("SubnetIdentifier")
            for subnet in subnets
            if subnet.get("SubnetIdentifier")
        ]