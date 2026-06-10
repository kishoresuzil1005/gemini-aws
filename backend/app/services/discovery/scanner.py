import logging
from typing import List, Dict, Any

from app.providers.aws.account import AccountDiscovery
from app.providers.aws.regions import RegionsDiscovery
from app.providers.aws.ec2 import EC2Discovery
from app.providers.aws.rds import RDSDiscovery
from app.providers.aws.s3 import S3Discovery
from app.providers.aws.lambda import LambdaDiscovery
from app.providers.aws.vpc import VPCDiscovery
from app.providers.aws.alb import ALBDiscovery
from app.providers.aws.ebs import EBSDiscovery
from app.providers.aws.ecs import ECSDiscovery
from app.providers.aws.eks import EKSDiscovery
from app.providers.aws.iam import IAMDiscovery

logger = logging.getLogger("AWS_Discovery_Scanner")

class AWSDiscoveryScanner:
    @staticmethod
    def scan_all(region: str = "us-east-1") -> List[Dict[str, Any]]:
        """
        Coordinates discovery of AWS resources using our modular provider adapters.
        """
        resources = []
        
        # 1. EC2 Instances
        try:
            ec2_instances = EC2Discovery.discover(region)
            for inst in ec2_instances:
                resources.append({
                    "provider": "AWS",

                    "id": inst["resource_id"],

                    "type": "EC2",

                    "name": f"EC2-{inst['resource_id'][-5:]}",

                    "status": inst["state"],

                    "region": region,

                    "instance_type":
                        inst.get("instance_type"),

                    "configuration_hint":
                        f"Instance Type: {inst.get('instance_type')} | Launch Time: {inst.get('launch_time')}"
                })
        except Exception as e:
            logger.warning(f"EC2 Discovery failed: {e}")

        # 2. S3 Buckets
        try:
            s3_buckets = S3Discovery.discover()
            for b in s3_buckets:
                resources.append({
                    "id": b["resource_id"],
                    "type": "S3",
                    "name": b["resource_id"],
                    "status": "active",
                    "region": region,
                    "configuration_hint": f"Created: {b.get('created')}"
                })
        except Exception as e:
            logger.warning(f"S3 Discovery failed: {e}")

        # 3. RDS Databases
        try:
            rds_db = RDSDiscovery.discover(region)
            for db in rds_db:
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
                        f"Engine: {db.get('engine')} | Class: {db.get('class')} | Multi-AZ: {db.get('multi_az')}"
                })
        except Exception as e:
            logger.warning(f"RDS Discovery failed: {e}")

        # 4. Lambda Functions
        try:
            lambdas = LambdaDiscovery.discover(region)
            for lf in lambdas:
                resources.append({
                    "provider": "AWS",

                    "id": lf["resource_id"],

                    "type": "Lambda",

                    "name": lf["resource_id"],

                    "status": "active",

                    "region": region,

                    "memory_size":
                        lf.get("memory_size"),

                    "configuration_hint":
                        f"Runtime: {lf.get('runtime')} | Memory: {lf.get('memory_size')}MB"
})
        except Exception as e:
            logger.warning(f"Lambda Discovery failed: {e}")

        # 5. VPCs
        try:
            vpcs = VPCDiscovery.discover(region)
            for vpc in vpcs:
                resources.append({
                    "id": vpc["resource_id"],
                    "type": "VPC",
                    "name": f"VPC-{vpc['resource_id'][-5:]}",
                    "status": vpc["state"],
                    "region": region,
                    "configuration_hint": f"CIDR Block: {vpc.get('cidr_block')} | Default VPC: {vpc.get('is_default')}"
                })
        except Exception as e:
            logger.warning(f"VPC Discovery failed: {e}")

        # 6. Load Balancers
        try:
            albs = ALBDiscovery.discover(region)
            for alb in albs:
                resources.append({
                    "id": alb["resource_id"],
                    "type": "ALB",
                    "name": alb["resource_id"],
                    "status": alb["state"] or "active",
                    "region": region,
                    "configuration_hint": f"DNS: {alb.get('dns_name')} | Scheme: {alb.get('scheme')}"
                })
        except Exception as e:
            logger.warning(f"ALB Discovery failed: {e}")

        # 7. EBS Volumes
        try:
            ebs_vols = EBSDiscovery.discover(region)
            for eb in ebs_vols:
                resources.append({
                    "provider": "AWS",

                    "id": eb["resource_id"],

                    "type": "EBS",

                    "name": f"Volume-{eb['resource_id'][-5:]}",

                    "status": eb["state"],

                    "region": region,

                    "size_gb":
                        eb.get("size_gb"),

                    "configuration_hint":
                        f"Size: {eb.get('size_gb')}GB | Attachments: {eb.get('attachments')}"
                })
        except Exception as e:
            logger.warning(f"EBS Discovery failed: {e}")

        # 8. ECS Clusters
        try:
            ecs_clusters = ECSDiscovery.discover(region)
            for cl in ecs_clusters:
                resources.append({
                    "id": cl["resource_id"],
                    "type": "ECS",
                    "name": cl["resource_id"],
                    "status": "active",
                    "region": region,
                    "configuration_hint": f"ARN: {cl.get('arn')}"
                })
        except Exception as e:
            logger.warning(f"ECS Discovery failed: {e}")

        # 9. EKS Clusters
        try:
            eks_clusters = EKSDiscovery.discover(region)
            for cl in eks_clusters:
                resources.append({
                    "id": cl["resource_id"],
                    "type": "EKS",
                    "name": cl["resource_id"],
                    "status": "active",
                    "region": region,
                    "configuration_hint": "Managed Kubernetes Cluster"
                })
        except Exception as e:
            logger.warning(f"EKS Discovery failed: {e}")

        # 10. IAM Users
        try:
            iam_users = IAMDiscovery.discover()
            for u in iam_users:
                resources.append({
                    "id": u["resource_id"],
                    "type": "IAM",
                    "name": u["resource_id"],
                    "status": "active",
                    "region": "global",
                    "configuration_hint": f"Created: {u.get('created')} | UserID: {u.get('user_id')}"
                })
        except Exception as e:
            logger.warning(f"IAM Discovery failed: {e}")

        return resources
