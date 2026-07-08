from typing import List, Any
from app.models import ResourceDB

class GraphMetadataHelper:
    """Extracts properties from Metadata V2 for builders to consume as a flat API."""

    @staticmethod
    def get_vpc_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        config = metadata.get("configuration", {})
        # Check both direct config (EC2/ALB) and vpc_config (Lambda)
        if config.get("vpc_id"):
            return config.get("vpc_id")
        vpc_config = config.get("vpc_config", {})
        if isinstance(vpc_config, dict):
            return vpc_config.get("VpcId") or vpc_config.get("vpc_id")
        return None

    @staticmethod
    def get_subnet_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        config = metadata.get("configuration", {})
        return config.get("subnet_id")

    @staticmethod
    def get_subnet_ids(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        config = metadata.get("configuration", {})
        vpc_config = config.get("vpc_config", {})
        if isinstance(vpc_config, dict) and vpc_config.get("SubnetIds"):
            return vpc_config.get("SubnetIds")
        # For ALB, it's inside availability_zones or subnets
        subnets = config.get("subnets", [])
        return subnets

    @staticmethod
    def get_security_groups(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        security = metadata.get("security", {})
        # EC2/ALB uses 'security_groups', RDS uses 'vpc_security_groups'
        sgs = security.get("security_groups") or security.get("vpc_security_groups", [])
        if not sgs:
            # Lambda uses SecurityGroupIds in vpc_config
            config = metadata.get("configuration", {})
            vpc_config = config.get("vpc_config", {})
            if isinstance(vpc_config, dict):
                sgs = vpc_config.get("SecurityGroupIds", [])
        return sgs

    @staticmethod
    def get_ebs_volumes(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {}).get("ebs_volumes", [])

    @staticmethod
    def get_iam_profile_or_role(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        security = metadata.get("security", {})
        return security.get("iam_instance_profile") or security.get("role")

    @staticmethod
    def get_target_groups(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {}).get("target_groups", [])
        
    @staticmethod
    def get_load_balancers(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {}).get("load_balancers", [])

    @staticmethod
    def get_targets(resource: ResourceDB) -> List[Dict[str, Any]]:
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {}).get("targets", [])

    @staticmethod
    def get_route_table_subnets(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {}).get("subnets", [])

    @staticmethod
    def get_route_table_igws(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {}).get("internet_gateways", [])

    @staticmethod
    def get_route_table_nat_gateways(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {}).get("nat_gateways", [])

    @staticmethod
    def get_instance_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {}).get("instance_id")

    @staticmethod
    def get_eni_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {}).get("network_interface_id")

    @staticmethod
    def get_referenced_security_groups(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        security = metadata.get("security", {})
        sgs = set()
        for rule in security.get("ingress_rules", []) + security.get("egress_rules", []):
            for pair in rule.get("UserIdGroupPairs", []):
                if pair.get("GroupId"):
                    sgs.add(pair.get("GroupId"))
        return list(sgs)
