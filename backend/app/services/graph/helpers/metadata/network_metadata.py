from typing import List, Dict, Any
from app.models import ResourceDB

class NetworkMetadata:
    """Extracts properties strictly matching the flat Network schema (Subnet, VPC, SG, etc.) in PostgreSQL."""

    @staticmethod
    def get_vpc_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("vpc_id")

    @staticmethod
    def get_subnet_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("subnet_id")

    @staticmethod
    def get_referenced_security_groups(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}

        ingress = metadata.get("ingress_rules") or []
        egress = metadata.get("egress_rules") or []

        if not isinstance(ingress, list):
            ingress = []

        if not isinstance(egress, list):
            egress = []

        sgs = set()

        for rule in ingress + egress:
            if not isinstance(rule, dict):
                continue

            for pair in rule.get("UserIdGroupPairs", []):
                if isinstance(pair, dict) and pair.get("GroupId"):
                    sgs.add(pair["GroupId"])

        return list(sgs)

    @staticmethod
    def get_security_groups(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("security_groups", [])

    @staticmethod
    def get_route_table_subnets(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("subnets", [])

    @staticmethod
    def get_route_table_igws(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("internet_gateways", [])

    @staticmethod
    def get_route_table_nat_gateways(resource: ResourceDB) -> List[str]:
        metadata = resource.resource_metadata or {}
        return metadata.get("nat_gateways", [])
        
    @staticmethod
    def get_eni_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("network_interface_id")

    @staticmethod
    def get_instance_id(resource: ResourceDB) -> str:
        metadata = resource.resource_metadata or {}
        return metadata.get("instance_id")