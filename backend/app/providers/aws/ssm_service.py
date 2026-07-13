"""SSM Service — Production (Parameter Store, Run Command, Session Manager)"""
import logging
import time
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class SsmService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("ssm", region_name=self.region, role_arn=self.role_arn)

    def list(self) -> List[Dict[str, Any]]:
        return self.list_managed_instances()

    # ─── Parameter Store ─────────────────────────────────────────────────────────

    def get_parameter(self, name: str, with_decryption: bool = True) -> Optional[Dict[str, Any]]:
        try:
            resp = self._client().get_parameter(Name=name, WithDecryption=with_decryption)
            return resp.get("Parameter")
        except self._client().exceptions.ParameterNotFound:
            return None

    def put_parameter(self, name: str, value: str, param_type: str = "SecureString", overwrite: bool = False, description: str = "") -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "Name": name,
            "Value": value,
            "Type": param_type,
            "Overwrite": overwrite,
        }
        if description:
            kwargs["Description"] = description
        resp = self._client().put_parameter(**kwargs)
        return {"version": resp.get("Version"), "tier": resp.get("Tier"), "status": "created"}

    def get_parameters_by_path(self, path: str, recursive: bool = True, with_decryption: bool = True) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("get_parameters_by_path")
        params = []
        for page in paginator.paginate(Path=path, Recursive=recursive, WithDecryption=with_decryption):
            params.extend(page.get("Parameters", []))
        return params

    def list_parameters(self, filters: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("describe_parameters")
        kwargs: Dict[str, Any] = {}
        if filters:
            kwargs["ParameterFilters"] = filters
        params = []
        for page in paginator.paginate(**kwargs):
            params.extend(page.get("Parameters", []))
        return params

    def delete_parameter(self, name: str) -> Dict[str, Any]:
        self._client().delete_parameter(Name=name)
        return {"status": "deleted", "name": name}

    # ─── Run Command ─────────────────────────────────────────────────────────────

    def run_command(self, instance_ids: List[str], commands: List[str], document_name: str = "AWS-RunShellScript", timeout_seconds: int = 60, comment: str = "") -> Dict[str, Any]:
        resp = self._client().send_command(
            InstanceIds=instance_ids,
            DocumentName=document_name,
            Parameters={"commands": commands},
            TimeoutSeconds=timeout_seconds,
            Comment=comment,
        )
        cmd = resp.get("Command", {})
        return {
            "command_id": cmd.get("CommandId"),
            "status": cmd.get("Status"),
            "instance_ids": instance_ids,
            "document_name": document_name,
        }

    def get_command_invocation(self, command_id: str, instance_id: str) -> Dict[str, Any]:
        resp = self._client().get_command_invocation(CommandId=command_id, InstanceId=instance_id)
        return {
            "status": resp.get("Status"),
            "status_details": resp.get("StatusDetails"),
            "standard_output": resp.get("StandardOutputContent", ""),
            "standard_error": resp.get("StandardErrorContent", ""),
            "response_code": resp.get("ResponseCode"),
        }

    def wait_for_command(self, command_id: str, instance_id: str, max_wait_seconds: int = 300, poll_interval: int = 5) -> Dict[str, Any]:
        elapsed = 0
        while elapsed < max_wait_seconds:
            result = self.get_command_invocation(command_id, instance_id)
            if result["status"] not in ("Pending", "InProgress", "Delayed"):
                return result
            time.sleep(poll_interval)
            elapsed += poll_interval
        return {"status": "TimedOut", "command_id": command_id}

    # ─── Managed Instances ────────────────────────────────────────────────────────

    def list_managed_instances(self) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("describe_instance_information")
        instances = []
        for page in paginator.paginate():
            for inst in page.get("InstanceInformationList", []):
                instances.append({
                    "resource_id": inst.get("InstanceId"),
                    "resource_type": "SSMManagedInstance",
                    "name": inst.get("Name", inst.get("InstanceId")),
                    "region": self.region,
                    "status": inst.get("PingStatus", "unknown"),
                    "metadata": {
                        "agent_version": inst.get("AgentVersion"),
                        "platform_type": inst.get("PlatformType"),
                        "platform_name": inst.get("PlatformName"),
                        "platform_version": inst.get("PlatformVersion"),
                        "ip_address": inst.get("IPAddress"),
                        "computer_name": inst.get("ComputerName"),
                        "last_ping": str(inst.get("LastPingDateTime", "")),
                    },
                })
        return instances

    def list_sessions(self, state: str = "Active") -> List[Dict[str, Any]]:
        resp = self._client().describe_sessions(State=state)
        return resp.get("Sessions", [])
