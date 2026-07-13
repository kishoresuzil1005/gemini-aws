from typing import List
from app.models import ResourceDB


class RDSMetadata:
    """Extracts properties from RDS metadata."""

    @staticmethod
    def get_vpc_id(resource: ResourceDB):
        metadata = resource.resource_metadata or {}

        subnet_group = metadata.get("subnet_group")

        if not isinstance(subnet_group, dict):
            return None

        return subnet_group.get("VpcId")

    @staticmethod
    def get_security_groups(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}

        groups = metadata.get("vpc_security_groups", [])

        if not groups:
            return []

        if isinstance(groups[0], dict):
            return [
                sg.get("VpcSecurityGroupId")
                for sg in groups
                if isinstance(sg, dict) and sg.get("VpcSecurityGroupId")
            ]

        return groups

    @staticmethod
    def get_subnets(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}

        subnet_group = metadata.get("subnet_group")

        # Older inventory format:
        # "subnet_group": "cloudops-db-subnet"
        if isinstance(subnet_group, str):
            return []

        if not isinstance(subnet_group, dict):
            return []

        subnets = subnet_group.get("Subnets", [])

        return [
            subnet.get("SubnetIdentifier")
            for subnet in subnets
            if isinstance(subnet, dict) and subnet.get("SubnetIdentifier")
        ]