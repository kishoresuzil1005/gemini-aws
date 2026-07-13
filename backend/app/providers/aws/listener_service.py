"""Listener Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class ListenerService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("elbv2", region_name=self.region, role_arn=self.role_arn)

    def list(self, lb_arn: str) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("describe_listeners")
        listeners = []
        for page in paginator.paginate(LoadBalancerArn=lb_arn):
            for listener in page.get("Listeners", []):
                listeners.append({
                    "resource_id": listener["ListenerArn"],
                    "resource_type": "Listener",
                    "name": f"Listener:{listener.get('Port')}",
                    "region": self.region,
                    "status": "active",
                    "metadata": {
                        "protocol": listener.get("Protocol"),
                        "port": listener.get("Port"),
                        "ssl_policy": listener.get("SslPolicy"),
                        "default_actions": listener.get("DefaultActions", []),
                        "certificates": listener.get("Certificates", []),
                        "lb_arn": lb_arn,
                    },
                })
        return listeners

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_listeners(ListenerArns=[resource_id])
        listeners = resp.get("Listeners", [])
        return listeners[0] if listeners else None

    def create(self, lb_arn: str, protocol: str, port: int, default_actions: List[Dict], ssl_policy: Optional[str] = None, certificates: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "LoadBalancerArn": lb_arn,
            "Protocol": protocol,
            "Port": port,
            "DefaultActions": default_actions,
        }
        if ssl_policy:
            kwargs["SslPolicy"] = ssl_policy
        if certificates:
            kwargs["Certificates"] = certificates
        resp = self._client().create_listener(**kwargs)
        listeners = resp.get("Listeners", [])
        return listeners[0] if listeners else {}

    def modify(self, listener_arn: str, default_actions: Optional[List[Dict]] = None, port: Optional[int] = None, protocol: Optional[str] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"ListenerArn": listener_arn}
        if default_actions:
            kwargs["DefaultActions"] = default_actions
        if port:
            kwargs["Port"] = port
        if protocol:
            kwargs["Protocol"] = protocol
        resp = self._client().modify_listener(**kwargs)
        listeners = resp.get("Listeners", [])
        return listeners[0] if listeners else {}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self._client().delete_listener(ListenerArn=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
