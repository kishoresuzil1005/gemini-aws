"""Autoscaling Group Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class AutoscalingService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("autoscaling", region_name=self.region, role_arn=self.role_arn)

    def list(self) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("describe_auto_scaling_groups")
        groups = []
        for page in paginator.paginate():
            for asg in page.get("AutoScalingGroups", []):
                groups.append({
                    "resource_id": asg["AutoScalingGroupARN"],
                    "resource_type": "AutoScalingGroup",
                    "name": asg["AutoScalingGroupName"],
                    "region": self.region,
                    "status": asg.get("Status", "active"),
                    "metadata": {
                        "min_size": asg.get("MinSize"),
                        "max_size": asg.get("MaxSize"),
                        "desired_capacity": asg.get("DesiredCapacity"),
                        "vpc_zone_identifier": asg.get("VPCZoneIdentifier"),
                        "health_check_type": asg.get("HealthCheckType"),
                        "launch_template": asg.get("LaunchTemplate", {}),
                        "instances": [
                            {"id": i["InstanceId"], "state": i.get("LifecycleState"), "health": i.get("HealthStatus")}
                            for i in asg.get("Instances", [])
                        ],
                        "load_balancer_names": asg.get("LoadBalancerNames", []),
                        "target_group_arns": asg.get("TargetGroupARNs", []),
                        "tags": {t["Key"]: t["Value"] for t in asg.get("Tags", [])},
                    },
                })
        return groups

    def get(self, group_name: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_auto_scaling_groups(AutoScalingGroupNames=[group_name])
        asgs = resp.get("AutoScalingGroups", [])
        return asgs[0] if asgs else None

    def set_desired_capacity(self, group_name: str, desired: int, honor_cooldown: bool = False) -> Dict[str, Any]:
        self._client().set_desired_capacity(
            AutoScalingGroupName=group_name,
            DesiredCapacity=desired,
            HonorCooldown=honor_cooldown,
        )
        return {"status": "updated", "group_name": group_name, "desired_capacity": desired}

    def list_policies(self, group_name: str) -> List[Dict[str, Any]]:
        resp = self._client().describe_policies(AutoScalingGroupName=group_name)
        return resp.get("ScalingPolicies", [])

    def list_activities(self, group_name: str, max_records: int = 20) -> List[Dict[str, Any]]:
        resp = self._client().describe_scaling_activities(
            AutoScalingGroupName=group_name, MaxRecords=max_records
        )
        return resp.get("Activities", [])

    def suspend_processes(self, group_name: str, scaling_processes: Optional[List[str]] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"AutoScalingGroupName": group_name}
        if scaling_processes:
            kwargs["ScalingProcesses"] = scaling_processes
        self._client().suspend_processes(**kwargs)
        return {"status": "processes_suspended", "group_name": group_name}

    def resume_processes(self, group_name: str, scaling_processes: Optional[List[str]] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"AutoScalingGroupName": group_name}
        if scaling_processes:
            kwargs["ScalingProcesses"] = scaling_processes
        self._client().resume_processes(**kwargs)
        return {"status": "processes_resumed", "group_name": group_name}

    def delete(self, resource_id: str, force_delete: bool = False) -> Dict[str, Any]:
        self._client().delete_auto_scaling_group(
            AutoScalingGroupName=resource_id, ForceDelete=force_delete
        )
        return {"status": "deleted", "resource_id": resource_id}
