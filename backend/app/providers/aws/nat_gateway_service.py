"""NAT Gateway Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class NatGatewayService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("ec2", region_name=self.region, role_arn=self.role_arn)

    def list(self) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("describe_nat_gateways")
        gateways = []
        for page in paginator.paginate():
            for ngw in page.get("NatGateways", []):
                gateways.append({
                    "resource_id": ngw["NatGatewayId"],
                    "resource_type": "NatGateway",
                    "name": next((t["Value"] for t in ngw.get("Tags", []) if t["Key"] == "Name"), ngw["NatGatewayId"]),
                    "region": self.region,
                    "status": ngw.get("State", "unknown"),
                    "metadata": {
                        "subnet_id": ngw.get("SubnetId"),
                        "vpc_id": ngw.get("VpcId"),
                        "connectivity_type": ngw.get("ConnectivityType"),
                        "nat_gateway_addresses": ngw.get("NatGatewayAddresses", []),
                        "tags": {t["Key"]: t["Value"] for t in ngw.get("Tags", [])},
                    },
                })
        return gateways

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_nat_gateways(NatGatewayIds=[resource_id])
        ngws = resp.get("NatGateways", [])
        return ngws[0] if ngws else None

    def create(self, subnet_id: str, allocation_id: str, connectivity_type: str = "public", tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "SubnetId": subnet_id,
            "AllocationId": allocation_id,
            "ConnectivityType": connectivity_type,
        }
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "natgateway", "Tags": tags}]
        resp = self._client().create_nat_gateway(**kwargs)
        return resp.get("NatGateway", {})

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self._client().delete_nat_gateway(NatGatewayId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
