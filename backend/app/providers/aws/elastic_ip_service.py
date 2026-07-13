"""Elastic IP Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class ElasticIpService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("ec2", region_name=self.region, role_arn=self.role_arn)

    def list(self) -> List[Dict[str, Any]]:
        resp = self._client().describe_addresses()
        return [
            {
                "resource_id": addr.get("AllocationId", addr.get("PublicIp")),
                "resource_type": "ElasticIp",
                "name": next((t["Value"] for t in addr.get("Tags", []) if t["Key"] == "Name"), addr.get("PublicIp", "")),
                "region": self.region,
                "status": "associated" if addr.get("AssociationId") else "unassociated",
                "metadata": {
                    "public_ip": addr.get("PublicIp"),
                    "private_ip": addr.get("PrivateIpAddress"),
                    "instance_id": addr.get("InstanceId"),
                    "allocation_id": addr.get("AllocationId"),
                    "association_id": addr.get("AssociationId"),
                    "network_interface_id": addr.get("NetworkInterfaceId"),
                    "domain": addr.get("Domain"),
                    "tags": {t["Key"]: t["Value"] for t in addr.get("Tags", [])},
                },
            }
            for addr in resp.get("Addresses", [])
        ]

    def get(self, allocation_id: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_addresses(AllocationIds=[allocation_id])
        addrs = resp.get("Addresses", [])
        return addrs[0] if addrs else None

    def allocate(self, domain: str = "vpc", tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"Domain": domain}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "elastic-ip", "Tags": tags}]
        resp = self._client().allocate_address(**kwargs)
        return resp

    def associate(self, allocation_id: str, instance_id: Optional[str] = None, network_interface_id: Optional[str] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"AllocationId": allocation_id}
        if instance_id:
            kwargs["InstanceId"] = instance_id
        if network_interface_id:
            kwargs["NetworkInterfaceId"] = network_interface_id
        resp = self._client().associate_address(**kwargs)
        return {"association_id": resp.get("AssociationId"), "status": "associated"}

    def disassociate(self, association_id: str) -> Dict[str, Any]:
        self._client().disassociate_address(AssociationId=association_id)
        return {"status": "disassociated", "association_id": association_id}

    def release(self, allocation_id: str) -> Dict[str, Any]:
        self._client().release_address(AllocationId=allocation_id)
        return {"status": "released", "allocation_id": allocation_id}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        return self.release(resource_id)
