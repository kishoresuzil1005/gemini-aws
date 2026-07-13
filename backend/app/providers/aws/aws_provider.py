"""
AWS Provider — Production Implementation
Orchestrates all AWS service calls through a unified BaseCloudProvider interface.
"""
import logging
import time
from typing import Any, Dict, List, Optional

from app.providers.base_provider import BaseCloudProvider
from app.providers.common.client_factory import client_factory
from app.providers.common.region_manager import region_manager
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider

logger = logging.getLogger(__name__)


class AWSProvider(BaseCloudProvider):
    """
    Production AWS provider.
    Wires discover(), get_resource(), list_resources(), execute_action(), health(), metrics()
    to real boto3 SDK calls.
    """

    def __init__(self, region: Optional[str] = None, role_arn: Optional[str] = None):
        self.region = region or region_manager.get_default_region("aws")
        self.role_arn = role_arn
        self._metrics: Dict[str, int] = {"api_calls": 0, "errors": 0, "retries": 0}

    @property
    def name(self) -> CloudProvider:
        return CloudProvider.AWS

    # ─── DISCOVERY ──────────────────────────────────────────────────────────────

    def discover(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """Discovers all supported resource types across the given region."""
        target_region = region or self.region
        resources: List[Dict[str, Any]] = []

        discovery_map = {
            "ec2": self._discover_ec2,
            "s3": self._discover_s3,
            "rds": self._discover_rds,
            "vpc": self._discover_vpc,
            "elb": self._discover_load_balancers,
            "lambda": self._discover_lambda,
        }

        for svc_name, fn in discovery_map.items():
            try:
                results = fn(target_region)
                resources.extend(results)
                logger.info(f"[AWS/{target_region}] Discovered {len(results)} {svc_name} resources.")
            except Exception as e:
                logger.error(f"[AWS/{target_region}] {svc_name} discovery failed: {e}")
                self._metrics["errors"] += 1

        return resources

    def _discover_ec2(self, region: str) -> List[Dict[str, Any]]:
        ec2 = client_factory.get_aws_client("ec2", region_name=region, role_arn=self.role_arn)
        self._metrics["api_calls"] += 1
        paginator = ec2.get_paginator("describe_instances")
        instances = []
        for page in paginator.paginate():
            for reservation in page.get("Reservations", []):
                for inst in reservation.get("Instances", []):
                    name = next((t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"), inst["InstanceId"])
                    instances.append({
                        "resource_id": inst["InstanceId"],
                        "resource_type": "EC2",
                        "name": name,
                        "region": region,
                        "status": inst.get("State", {}).get("Name", "unknown"),
                        "metadata": {
                            "instance_type": inst.get("InstanceType"),
                            "private_ip": inst.get("PrivateIpAddress"),
                            "public_ip": inst.get("PublicIpAddress"),
                            "vpc_id": inst.get("VpcId"),
                            "subnet_id": inst.get("SubnetId"),
                            "launch_time": str(inst.get("LaunchTime", "")),
                            "ami_id": inst.get("ImageId"),
                            "key_name": inst.get("KeyName"),
                            "iam_profile": inst.get("IamInstanceProfile", {}).get("Arn"),
                            "security_groups": [sg["GroupId"] for sg in inst.get("SecurityGroups", [])],
                            "tags": {t["Key"]: t["Value"] for t in inst.get("Tags", [])},
                        },
                    })
        return instances

    def _discover_s3(self, region: str) -> List[Dict[str, Any]]:
        s3 = client_factory.get_aws_client("s3", region_name=region, role_arn=self.role_arn)
        self._metrics["api_calls"] += 1
        resp = s3.list_buckets()
        buckets = []
        for bucket in resp.get("Buckets", []):
            name = bucket["Name"]
            try:
                location = s3.get_bucket_location(Bucket=name).get("LocationConstraint") or "us-east-1"
            except Exception:
                location = "unknown"
            buckets.append({
                "resource_id": name,
                "resource_type": "S3",
                "name": name,
                "region": location,
                "status": "active",
                "metadata": {"creation_date": str(bucket.get("CreationDate", ""))},
            })
        return buckets

    def _discover_rds(self, region: str) -> List[Dict[str, Any]]:
        rds = client_factory.get_aws_client("rds", region_name=region, role_arn=self.role_arn)
        self._metrics["api_calls"] += 1
        paginator = rds.get_paginator("describe_db_instances")
        instances = []
        for page in paginator.paginate():
            for db in page.get("DBInstances", []):
                instances.append({
                    "resource_id": db["DBInstanceIdentifier"],
                    "resource_type": "RDS",
                    "name": db["DBInstanceIdentifier"],
                    "region": region,
                    "status": db.get("DBInstanceStatus", "unknown"),
                    "metadata": {
                        "engine": db.get("Engine"),
                        "engine_version": db.get("EngineVersion"),
                        "instance_class": db.get("DBInstanceClass"),
                        "multi_az": db.get("MultiAZ"),
                        "storage_encrypted": db.get("StorageEncrypted"),
                        "endpoint": db.get("Endpoint", {}).get("Address"),
                        "vpc_id": db.get("DBSubnetGroup", {}).get("VpcId"),
                    },
                })
        return instances

    def _discover_vpc(self, region: str) -> List[Dict[str, Any]]:
        ec2 = client_factory.get_aws_client("ec2", region_name=region, role_arn=self.role_arn)
        self._metrics["api_calls"] += 1
        resp = ec2.describe_vpcs()
        return [
            {
                "resource_id": vpc["VpcId"],
                "resource_type": "VPC",
                "name": next((t["Value"] for t in vpc.get("Tags", []) if t["Key"] == "Name"), vpc["VpcId"]),
                "region": region,
                "status": vpc.get("State", "available"),
                "metadata": {
                    "cidr_block": vpc.get("CidrBlock"),
                    "is_default": vpc.get("IsDefault"),
                    "dhcp_options_id": vpc.get("DhcpOptionsId"),
                    "tags": {t["Key"]: t["Value"] for t in vpc.get("Tags", [])},
                },
            }
            for vpc in resp.get("Vpcs", [])
        ]

    def _discover_load_balancers(self, region: str) -> List[Dict[str, Any]]:
        elbv2 = client_factory.get_aws_client("elbv2", region_name=region, role_arn=self.role_arn)
        self._metrics["api_calls"] += 1
        paginator = elbv2.get_paginator("describe_load_balancers")
        lbs = []
        for page in paginator.paginate():
            for lb in page.get("LoadBalancers", []):
                lbs.append({
                    "resource_id": lb["LoadBalancerArn"],
                    "resource_type": "ELB",
                    "name": lb["LoadBalancerName"],
                    "region": region,
                    "status": lb.get("State", {}).get("Code", "unknown"),
                    "metadata": {
                        "dns_name": lb.get("DNSName"),
                        "scheme": lb.get("Scheme"),
                        "type": lb.get("Type"),
                        "vpc_id": lb.get("VpcId"),
                    },
                })
        return lbs

    def _discover_lambda(self, region: str) -> List[Dict[str, Any]]:
        lmb = client_factory.get_aws_client("lambda", region_name=region, role_arn=self.role_arn)
        self._metrics["api_calls"] += 1
        paginator = lmb.get_paginator("list_functions")
        functions = []
        for page in paginator.paginate():
            for fn in page.get("Functions", []):
                functions.append({
                    "resource_id": fn["FunctionArn"],
                    "resource_type": "Lambda",
                    "name": fn["FunctionName"],
                    "region": region,
                    "status": "active",
                    "metadata": {
                        "runtime": fn.get("Runtime"),
                        "memory": fn.get("MemorySize"),
                        "timeout": fn.get("Timeout"),
                        "handler": fn.get("Handler"),
                        "role": fn.get("Role"),
                        "last_modified": fn.get("LastModified"),
                    },
                })
        return functions

    # ─── RESOURCE GET / LIST ─────────────────────────────────────────────────────

    def get_resource(self, resource_type: str, resource_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        region = kwargs.get("region", self.region)
        self._metrics["api_calls"] += 1
        try:
            rt = resource_type.lower()
            if rt == "ec2":
                ec2 = client_factory.get_aws_client("ec2", region_name=region, role_arn=self.role_arn)
                resp = ec2.describe_instances(InstanceIds=[resource_id])
                reservations = resp.get("Reservations", [])
                if reservations:
                    return reservations[0]["Instances"][0]
            elif rt == "s3":
                s3 = client_factory.get_aws_client("s3", region_name=region, role_arn=self.role_arn)
                return s3.head_bucket(Bucket=resource_id)
            elif rt == "rds":
                rds = client_factory.get_aws_client("rds", region_name=region, role_arn=self.role_arn)
                resp = rds.describe_db_instances(DBInstanceIdentifier=resource_id)
                dbs = resp.get("DBInstances", [])
                return dbs[0] if dbs else None
        except Exception as e:
            logger.error(f"get_resource({resource_type}, {resource_id}) failed: {e}")
            self._metrics["errors"] += 1
        return None

    def list_resources(self, resource_type: str, **kwargs) -> List[Dict[str, Any]]:
        region = kwargs.get("region", self.region)
        self._metrics["api_calls"] += 1
        rt = resource_type.lower()
        try:
            if rt == "ec2":
                return self._discover_ec2(region)
            elif rt == "s3":
                return self._discover_s3(region)
            elif rt == "rds":
                return self._discover_rds(region)
            elif rt == "vpc":
                return self._discover_vpc(region)
            elif rt in ("elb", "alb", "nlb"):
                return self._discover_load_balancers(region)
            elif rt == "lambda":
                return self._discover_lambda(region)
        except Exception as e:
            logger.error(f"list_resources({resource_type}) failed: {e}")
            self._metrics["errors"] += 1
        return []

    # ─── ACTIONS ────────────────────────────────────────────────────────────────

    def execute_action(self, action: str, resource_id: str, **kwargs) -> Dict[str, Any]:
        region = kwargs.get("region", self.region)
        self._metrics["api_calls"] += 1
        resource_type = kwargs.get("resource_type", "ec2").lower()

        try:
            if resource_type == "ec2":
                ec2 = client_factory.get_aws_client("ec2", region_name=region, role_arn=self.role_arn)
                action_map = {
                    "start": ec2.start_instances,
                    "stop": ec2.stop_instances,
                    "reboot": ec2.reboot_instances,
                    "terminate": ec2.terminate_instances,
                }
                if action in action_map:
                    resp = action_map[action](InstanceIds=[resource_id])
                    return {"status": "success", "action": action, "resource_id": resource_id, "response": str(resp)}

            elif resource_type == "rds":
                rds = client_factory.get_aws_client("rds", region_name=region, role_arn=self.role_arn)
                if action == "stop":
                    rds.stop_db_instance(DBInstanceIdentifier=resource_id)
                elif action == "start":
                    rds.start_db_instance(DBInstanceIdentifier=resource_id)
                elif action == "reboot":
                    rds.reboot_db_instance(DBInstanceIdentifier=resource_id)
                return {"status": "success", "action": action, "resource_id": resource_id}

        except Exception as e:
            logger.error(f"execute_action({action}, {resource_id}) failed: {e}")
            self._metrics["errors"] += 1
            return {"status": "error", "error": str(e), "action": action, "resource_id": resource_id}

        return {"status": "unsupported", "action": action, "resource_type": resource_type}

    def delete(self, resource_type: str, resource_id: str, **kwargs) -> Dict[str, Any]:
        region = kwargs.get("region", self.region)
        self._metrics["api_calls"] += 1
        try:
            rt = resource_type.lower()
            if rt == "ec2":
                ec2 = client_factory.get_aws_client("ec2", region_name=region, role_arn=self.role_arn)
                ec2.terminate_instances(InstanceIds=[resource_id])
            elif rt == "s3":
                s3 = client_factory.get_aws_client("s3", region_name=region, role_arn=self.role_arn)
                s3.delete_bucket(Bucket=resource_id)
            return {"status": "deleted", "resource_id": resource_id, "resource_type": resource_type}
        except Exception as e:
            logger.error(f"delete({resource_type}, {resource_id}) failed: {e}")
            self._metrics["errors"] += 1
            return {"status": "error", "error": str(e)}

    # ─── HEALTH & METRICS ────────────────────────────────────────────────────────

    def health(self) -> Dict[str, Any]:
        try:
            ec2 = client_factory.get_aws_client("ec2", region_name=self.region, role_arn=self.role_arn)
            ec2.describe_availability_zones()
            return {
                "status": "healthy",
                "provider": "aws",
                "region": self.region,
                "auth": "valid",
                "timestamp": time.time(),
            }
        except Exception as e:
            return {"status": "unhealthy", "provider": "aws", "error": str(e), "timestamp": time.time()}

    def metrics(self) -> Dict[str, Any]:
        return {**self._metrics, "provider": "aws", "region": self.region}

    # ─── CAPABILITIES ────────────────────────────────────────────────────────────

    def capabilities(self) -> List[str]:
        return ["ec2", "s3", "vpc", "rds", "lambda", "elb", "ecs", "eks", "cloudwatch",
                "iam", "route53", "cloudfront", "autoscaling", "sqs", "sns", "dynamodb"]

    def discover_capabilities(self) -> List[str]:
        """Queries AWS Resource Groups Tagging API to find resource types in this account/region."""
        try:
            rgt = client_factory.get_aws_client("resourcegroupstaggingapi", region_name=self.region, role_arn=self.role_arn)
            paginator = rgt.get_paginator("get_resources")
            resource_types = set()
            for page in paginator.paginate():
                for res in page.get("ResourceTagMappingList", []):
                    arn_parts = res.get("ResourceARN", "").split(":")
                    if len(arn_parts) >= 3:
                        resource_types.add(arn_parts[2])
            return list(resource_types) or self.capabilities()
        except Exception as e:
            logger.warning(f"discover_capabilities failed, using static list: {e}")
            return self.capabilities()
