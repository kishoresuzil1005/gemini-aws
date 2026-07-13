"""Network Interface Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class NetworkInterfaceService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("ec2", region_name=self.region, role_arn=self.role_arn)

    def list(self, vpc_id: Optional[str] = None, subnet_id: Optional[str] = None) -> List[Dict[str, Any]]:
        filters = []
        if vpc_id:
            filters.append({"Name": "vpc-id", "Values": [vpc_id]})
        if subnet_id:
            filters.append({"Name": "subnet-id", "Values": [subnet_id]})
        kwargs: Dict[str, Any] = {"Filters": filters} if filters else {}
        paginator = self._client().get_paginator("describe_network_interfaces")
        interfaces = []
        for page in paginator.paginate(**kwargs):
            for eni in page.get("NetworkInterfaces", []):
                interfaces.append({
                    "resource_id": eni["NetworkInterfaceId"],
                    "resource_type": "NetworkInterface",
                    "name": next((t["Value"] for t in eni.get("TagSet", []) if t["Key"] == "Name"), eni["NetworkInterfaceId"]),
                    "region": self.region,
                    "status": eni.get("Status", "unknown"),
                    "metadata": {
                        "vpc_id": eni.get("VpcId"),
                        "subnet_id": eni.get("SubnetId"),
                        "private_ip": eni.get("PrivateIpAddress"),
                        "mac_address": eni.get("MacAddress"),
                        "interface_type": eni.get("InterfaceType"),
                        "attachment": eni.get("Attachment", {}),
                        "groups": [g["GroupId"] for g in eni.get("Groups", [])],
                        "tags": {t["Key"]: t["Value"] for t in eni.get("TagSet", [])},
                    },
                })
        return interfaces

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_network_interfaces(NetworkInterfaceIds=[resource_id])
        enis = resp.get("NetworkInterfaces", [])
        return enis[0] if enis else None

    def create(self, subnet_id: str, description: str = "", groups: Optional[List[str]] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"SubnetId": subnet_id, "Description": description}
        if groups:
            kwargs["Groups"] = groups
        resp = self._client().create_network_interface(**kwargs)
        return resp.get("NetworkInterface", {})

    def attach(self, eni_id: str, instance_id: str, device_index: int) -> Dict[str, Any]:
        resp = self._client().attach_network_interface(
            NetworkInterfaceId=eni_id, InstanceId=instance_id, DeviceIndex=device_index
        )
        return {"attachment_id": resp.get("AttachmentId"), "status": "attached"}

    def detach(self, attachment_id: str, force: bool = False) -> Dict[str, Any]:
        self._client().detach_network_interface(AttachmentId=attachment_id, Force=force)
        return {"status": "detached", "attachment_id": attachment_id}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self._client().delete_network_interface(NetworkInterfaceId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
