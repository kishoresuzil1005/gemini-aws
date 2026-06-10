import logging
from typing import List, Dict, Any

from app.providers.aws.ec2 import EC2Discovery
from app.providers.aws.rds import RDSDiscovery
from app.providers.aws.s3 import S3Discovery
from app.providers.aws.lambda_discovery import LambdaDiscovery
from app.providers.aws.vpc import VPCDiscovery
from app.providers.aws.alb import ALBDiscovery
from app.providers.aws.ebs import EBSDiscovery
from app.providers.aws.ecs import ECSDiscovery
from app.providers.aws.eks import EKSDiscovery
from app.providers.aws.iam import IAMDiscovery

logger = logging.getLogger("AWS_Discovery_Scanner")


class AWSDiscoveryScanner:

    @staticmethod
    def scan_all(
        region: str = "us-east-1"
    ) -> List[Dict[str, Any]]:

        resources = []

        # EC2
        try:
            for inst in EC2Discovery.discover(region):

                resources.append({
                    "provider": "AWS",
                    "id": inst["resource_id"],
                    "type": "EC2",
                    "name": inst["resource_id"],
                    "status": inst["state"],
                    "region": region,

                    "instance_type":
                        inst.get("instance_type"),

                    "configuration_hint":
                        f"Type={inst.get('instance_type')} "
                        f"Launch={inst.get('launch_time')}"
                })

        except Exception as e:
            logger.warning(
                f"EC2 Discovery failed: {e}"
            )

        # S3
        try:
            for bucket in S3Discovery.discover():

                resources.append({
                    "provider": "AWS",
                    "id": bucket["resource_id"],
                    "type": "S3",
                    "name": bucket["resource_id"],
                    "status": "active",
                    "region": "global",

                    "size_gb": 0,

                    "configuration_hint":
                        f"Created={bucket.get('created')}"
                })

        except Exception as e:
            logger.warning(
                f"S3 Discovery failed: {e}"
            )

        # RDS
        try:
            for db in RDSDiscovery.discover(region):

                resources.append({
                    "provider": "AWS",
                    "id": db["resource_id"],
                    "type": "RDS",
                    "name": db["resource_id"],
                    "status": db["status"],
                    "region": region,

                    "instance_class":
                        db.get("class"),

                    "configuration_hint":
                        f"Engine={db.get('engine')} "
                        f"Class={db.get('class')}"
                })

        except Exception as e:
            logger.warning(
                f"RDS Discovery failed: {e}"
            )

        # Lambda
        try:
            for fn in LambdaDiscovery.discover(region):

                resources.append({
                    "provider": "AWS",
                    "id": fn["resource_id"],
                    "type": "Lambda",
                    "name": fn["resource_id"],
                    "status": "active",
                    "region": region,

                    "memory_size":
                        fn.get("memory_size"),

                    "configuration_hint":
                        f"Runtime={fn.get('runtime')} "
                        f"Memory={fn.get('memory_size')}MB"
                })

        except Exception as e:
            logger.warning(
                f"Lambda Discovery failed: {e}"
            )

        # VPC
        try:
            for vpc in VPCDiscovery.discover(region):

                resources.append({
                    "provider": "AWS",
                    "id": vpc["resource_id"],
                    "type": "VPC",
                    "name": vpc["resource_id"],
                    "status": vpc["state"],
                    "region": region
                })

        except Exception as e:
            logger.warning(
                f"VPC Discovery failed: {e}"
            )

        # ALB
        try:
            for alb in ALBDiscovery.discover(region):

                resources.append({
                    "provider": "AWS",
                    "id": alb["resource_id"],
                    "type": "ALB",
                    "name": alb["resource_id"],
                    "status":
                        alb.get("state", "active"),
                    "region": region
                })

        except Exception as e:
            logger.warning(
                f"ALB Discovery failed: {e}"
            )

        # EBS
        try:
            for vol in EBSDiscovery.discover(region):

                resources.append({
                    "provider": "AWS",
                    "id": vol["resource_id"],
                    "type": "EBS",
                    "name": vol["resource_id"],
                    "status": vol["state"],
                    "region": region,

                    "size_gb":
                        vol.get("size_gb"),

                    "configuration_hint":
                        f"Size={vol.get('size_gb')}GB"
                })

        except Exception as e:
            logger.warning(
                f"EBS Discovery failed: {e}"
            )

        # ECS
        try:
            for ecs in ECSDiscovery.discover(region):

                resources.append({
                    "provider": "AWS",
                    "id": ecs["resource_id"],
                    "type": "ECS",
                    "name": ecs["resource_id"],
                    "status": "active",
                    "region": region
                })

        except Exception as e:
            logger.warning(
                f"ECS Discovery failed: {e}"
            )

        # EKS
        try:
            for eks in EKSDiscovery.discover(region):

                resources.append({
                    "provider": "AWS",
                    "id": eks["resource_id"],
                    "type": "EKS",
                    "name": eks["resource_id"],
                    "status": "active",
                    "region": region
                })

        except Exception as e:
            logger.warning(
                f"EKS Discovery failed: {e}"
            )

        # IAM
        try:
            for user in IAMDiscovery.discover():

                resources.append({
                    "provider": "AWS",
                    "id": user["resource_id"],
                    "type": "IAM",
                    "name": user["resource_id"],
                    "status": "active",
                    "region": "global"
                })

        except Exception as e:
            logger.warning(
                f"IAM Discovery failed: {e}"
            )

        return resources