"""Target Group Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class TargetGroupService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("elbv2", region_name=self.region, role_arn=self.role_arn)

    def list(self, lb_arn: Optional[str] = None) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {}
        if lb_arn:
            kwargs["LoadBalancerArn"] = lb_arn
        paginator = self._client().get_paginator("describe_target_groups")
        groups = []
        for page in paginator.paginate(**kwargs):
            for tg in page.get("TargetGroups", []):
                groups.append({
                    "resource_id": tg["TargetGroupArn"],
                    "resource_type": "TargetGroup",
                    "name": tg.get("TargetGroupName"),
                    "region": self.region,
                    "status": "active",
                    "metadata": {
                        "protocol": tg.get("Protocol"),
                        "port": tg.get("Port"),
                        "vpc_id": tg.get("VpcId"),
                        "target_type": tg.get("TargetType"),
                        "health_check_protocol": tg.get("HealthCheckProtocol"),
                        "health_check_path": tg.get("HealthCheckPath"),
                        "matcher": tg.get("Matcher", {}),
                    },
                })
        return groups

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_target_groups(TargetGroupArns=[resource_id])
        tgs = resp.get("TargetGroups", [])
        return tgs[0] if tgs else None

    def get_target_health(self, tg_arn: str) -> List[Dict[str, Any]]:
        resp = self._client().describe_target_health(TargetGroupArn=tg_arn)
        return resp.get("TargetHealthDescriptions", [])

    def create(self, name: str, protocol: str, port: int, vpc_id: str, target_type: str = "instance") -> Dict[str, Any]:
        resp = self._client().create_target_group(
            Name=name, Protocol=protocol, Port=port, VpcId=vpc_id, TargetType=target_type
        )
        tgs = resp.get("TargetGroups", [])
        return tgs[0] if tgs else {}

    def register_targets(self, tg_arn: str, targets: List[Dict]) -> Dict[str, Any]:
        self._client().register_targets(TargetGroupArn=tg_arn, Targets=targets)
        return {"status": "targets_registered", "tg_arn": tg_arn}

    def deregister_targets(self, tg_arn: str, targets: List[Dict]) -> Dict[str, Any]:
        self._client().deregister_targets(TargetGroupArn=tg_arn, Targets=targets)
        return {"status": "targets_deregistered", "tg_arn": tg_arn}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self._client().delete_target_group(TargetGroupArn=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
