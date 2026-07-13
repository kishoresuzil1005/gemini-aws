"""Subnet Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class SubnetService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("ec2", region_name=self.region, role_arn=self.role_arn)

    def list(self, vpc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {}
        if vpc_id:
            kwargs["Filters"] = [{"Name": "vpc-id", "Values": [vpc_id]}]
        paginator = self._client().get_paginator("describe_subnets")
        subnets = []
        for page in paginator.paginate(**kwargs):
            for subnet in page.get("Subnets", []):
                subnets.append({
                    "resource_id": subnet["SubnetId"],
                    "resource_type": "Subnet",
                    "name": next((t["Value"] for t in subnet.get("Tags", []) if t["Key"] == "Name"), subnet["SubnetId"]),
                    "region": self.region,
                    "status": subnet.get("State", "available"),
                    "metadata": {
                        "vpc_id": subnet.get("VpcId"),
                        "cidr_block": subnet.get("CidrBlock"),
                        "availability_zone": subnet.get("AvailabilityZone"),
                        "available_ip_count": subnet.get("AvailableIpAddressCount"),
                        "map_public_ip": subnet.get("MapPublicIpOnLaunch"),
                        "tags": {t["Key"]: t["Value"] for t in subnet.get("Tags", [])},
                    },
                })
        return subnets

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_subnets(SubnetIds=[resource_id])
        subnets = resp.get("Subnets", [])
        return subnets[0] if subnets else None

    def create(self, vpc_id: str, cidr_block: str, availability_zone: str, tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"VpcId": vpc_id, "CidrBlock": cidr_block, "AvailabilityZone": availability_zone}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "subnet", "Tags": tags}]
        resp = self._client().create_subnet(**kwargs)
        return resp.get("Subnet", {})

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self._client().delete_subnet(SubnetId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
