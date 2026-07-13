"""Load Balancer Service — Production (ALB + NLB via elbv2)"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class LoadBalancerService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("elbv2", region_name=self.region, role_arn=self.role_arn)

    def list(self) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("describe_load_balancers")
        lbs = []
        for page in paginator.paginate():
            for lb in page.get("LoadBalancers", []):
                lbs.append({
                    "resource_id": lb["LoadBalancerArn"],
                    "resource_type": "LoadBalancer",
                    "name": lb.get("LoadBalancerName"),
                    "region": self.region,
                    "status": lb.get("State", {}).get("Code", "unknown"),
                    "metadata": {
                        "type": lb.get("Type"),
                        "scheme": lb.get("Scheme"),
                        "dns_name": lb.get("DNSName"),
                        "vpc_id": lb.get("VpcId"),
                        "ip_address_type": lb.get("IpAddressType"),
                        "availability_zones": [az["ZoneName"] for az in lb.get("AvailabilityZones", [])],
                        "created_time": str(lb.get("CreatedTime", "")),
                    },
                })
        return lbs

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_load_balancers(LoadBalancerArns=[resource_id])
        lbs = resp.get("LoadBalancers", [])
        return lbs[0] if lbs else None

    def create(self, name: str, subnets: List[str], lb_type: str = "application", scheme: str = "internet-facing", security_groups: Optional[List[str]] = None, tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"Name": name, "Subnets": subnets, "Type": lb_type, "Scheme": scheme}
        if security_groups:
            kwargs["SecurityGroups"] = security_groups
        if tags:
            kwargs["Tags"] = tags
        resp = self._client().create_load_balancer(**kwargs)
        lbs = resp.get("LoadBalancers", [])
        return lbs[0] if lbs else {}

    def describe_attributes(self, lb_arn: str) -> List[Dict[str, Any]]:
        resp = self._client().describe_load_balancer_attributes(LoadBalancerArn=lb_arn)
        return resp.get("Attributes", [])

    def modify_attribute(self, lb_arn: str, key: str, value: str) -> Dict[str, Any]:
        resp = self._client().modify_load_balancer_attributes(
            LoadBalancerArn=lb_arn,
            Attributes=[{"Key": key, "Value": value}],
        )
        return {"status": "modified", "attributes": resp.get("Attributes", [])}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self._client().delete_load_balancer(LoadBalancerArn=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
