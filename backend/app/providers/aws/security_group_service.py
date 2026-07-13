"""Security Group Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class SecurityGroupService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("ec2", region_name=self.region, role_arn=self.role_arn)

    def list(self, vpc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {}
        if vpc_id:
            kwargs["Filters"] = [{"Name": "vpc-id", "Values": [vpc_id]}]
        paginator = self._client().get_paginator("describe_security_groups")
        sgs = []
        for page in paginator.paginate(**kwargs):
            for sg in page.get("SecurityGroups", []):
                sgs.append({
                    "resource_id": sg["GroupId"],
                    "resource_type": "SecurityGroup",
                    "name": sg.get("GroupName"),
                    "region": self.region,
                    "status": "active",
                    "metadata": {
                        "description": sg.get("Description"),
                        "vpc_id": sg.get("VpcId"),
                        "ingress_rules": sg.get("IpPermissions", []),
                        "egress_rules": sg.get("IpPermissionsEgress", []),
                        "tags": {t["Key"]: t["Value"] for t in sg.get("Tags", [])},
                    },
                })
        return sgs

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_security_groups(GroupIds=[resource_id])
        sgs = resp.get("SecurityGroups", [])
        return sgs[0] if sgs else None

    def create(self, group_name: str, description: str, vpc_id: str, tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"GroupName": group_name, "Description": description, "VpcId": vpc_id}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "security-group", "Tags": tags}]
        resp = self._client().create_security_group(**kwargs)
        return {"group_id": resp.get("GroupId"), "status": "created"}

    def authorize_ingress(self, group_id: str, ip_permissions: List[Dict]) -> Dict[str, Any]:
        self._client().authorize_security_group_ingress(GroupId=group_id, IpPermissions=ip_permissions)
        return {"status": "ingress_authorized", "group_id": group_id}

    def authorize_egress(self, group_id: str, ip_permissions: List[Dict]) -> Dict[str, Any]:
        self._client().authorize_security_group_egress(GroupId=group_id, IpPermissions=ip_permissions)
        return {"status": "egress_authorized", "group_id": group_id}

    def revoke_ingress(self, group_id: str, ip_permissions: List[Dict]) -> Dict[str, Any]:
        self._client().revoke_security_group_ingress(GroupId=group_id, IpPermissions=ip_permissions)
        return {"status": "ingress_revoked", "group_id": group_id}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self._client().delete_security_group(GroupId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
