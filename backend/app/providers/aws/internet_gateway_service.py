"""Internet Gateway Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory
logger = logging.getLogger(__name__)

class InternetGatewayService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("ec2", region_name=self.region, role_arn=self.role_arn)

    def list(self) -> List[Dict[str, Any]]:
        resp = self._client().describe_internet_gateways()
        return [{"resource_id": igw["InternetGatewayId"], "resource_type": "InternetGateway", "name": next((t["Value"] for t in igw.get("Tags",[]) if t["Key"]=="Name"), igw["InternetGatewayId"]), "region": self.region, "status": "attached" if igw.get("Attachments") else "detached", "metadata": {"attachments": igw.get("Attachments",[]), "tags": {t["Key"]: t["Value"] for t in igw.get("Tags",[])}}} for igw in resp.get("InternetGateways",[])]

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_internet_gateways(InternetGatewayIds=[resource_id])
        igws = resp.get("InternetGateways", [])
        return igws[0] if igws else None

    def create(self, tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {}
        if tags: kwargs["TagSpecifications"] = [{"ResourceType": "internet-gateway", "Tags": tags}]
        return self._client().create_internet_gateway(**kwargs).get("InternetGateway", {})

    def attach(self, igw_id: str, vpc_id: str) -> Dict[str, Any]:
        self._client().attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        return {"status": "attached"}

    def detach(self, igw_id: str, vpc_id: str) -> Dict[str, Any]:
        self._client().detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        return {"status": "detached"}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self._client().delete_internet_gateway(InternetGatewayId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
