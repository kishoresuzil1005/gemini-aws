"""Route Table Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class RouteTableService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("ec2", region_name=self.region, role_arn=self.role_arn)

    def list(self, vpc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {}
        if vpc_id:
            kwargs["Filters"] = [{"Name": "vpc-id", "Values": [vpc_id]}]
        paginator = self._client().get_paginator("describe_route_tables")
        tables = []
        for page in paginator.paginate(**kwargs):
            for rt in page.get("RouteTables", []):
                tables.append({
                    "resource_id": rt["RouteTableId"],
                    "resource_type": "RouteTable",
                    "name": next((t["Value"] for t in rt.get("Tags", []) if t["Key"] == "Name"), rt["RouteTableId"]),
                    "region": self.region,
                    "status": "active",
                    "metadata": {
                        "vpc_id": rt.get("VpcId"),
                        "routes": rt.get("Routes", []),
                        "associations": rt.get("Associations", []),
                        "tags": {t["Key"]: t["Value"] for t in rt.get("Tags", [])},
                    },
                })
        return tables

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_route_tables(RouteTableIds=[resource_id])
        rts = resp.get("RouteTables", [])
        return rts[0] if rts else None

    def create(self, vpc_id: str, tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"VpcId": vpc_id}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "route-table", "Tags": tags}]
        resp = self._client().create_route_table(**kwargs)
        return resp.get("RouteTable", {})

    def create_route(self, route_table_id: str, destination_cidr: str, gateway_id: Optional[str] = None, nat_gateway_id: Optional[str] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"RouteTableId": route_table_id, "DestinationCidrBlock": destination_cidr}
        if gateway_id:
            kwargs["GatewayId"] = gateway_id
        if nat_gateway_id:
            kwargs["NatGatewayId"] = nat_gateway_id
        self._client().create_route(**kwargs)
        return {"status": "created", "route_table_id": route_table_id, "destination": destination_cidr}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self._client().delete_route_table(RouteTableId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
