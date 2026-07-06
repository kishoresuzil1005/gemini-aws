import logging
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any

from app.services.discovery.models import ScanResult

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
from app.providers.aws.igw import IGWDiscovery
from app.providers.aws.regions import get_all_regions
# Sprint 1 providers
from app.providers.aws.subnet import SubnetDiscovery
from app.providers.aws.security_group import SecurityGroupDiscovery
from app.providers.aws.route_table import RouteTableDiscovery
from app.providers.aws.nat_gateway import NatGatewayDiscovery
from app.providers.aws.network_interface import NetworkInterfaceDiscovery
from app.providers.aws.elastic_ip import ElasticIPDiscovery
from app.providers.aws.autoscaling import AutoScalingDiscovery
from app.providers.aws.target_group import TargetGroupDiscovery
# Phase 4 providers
from app.providers.aws.apigateway import APIGatewayDiscovery
from app.providers.aws.cloudfront import CloudFrontDiscovery
from app.providers.aws.route53 import Route53Discovery
from app.providers.aws.waf import WAFDiscovery
from app.providers.aws.secrets_manager import SecretsManagerDiscovery, SSMDiscovery
from app.providers.aws.sns import SNSDiscovery
from app.providers.aws.sqs import SQSDiscovery
from app.providers.aws.eventbridge import EventBridgeDiscovery
from app.providers.aws.dynamodb import DynamoDBDiscovery
from app.providers.aws.elasticache import ElastiCacheDiscovery
from app.providers.aws.opensearch import OpenSearchDiscovery
from app.providers.aws.efs import EFSDiscovery

logger = logging.getLogger("AWS_Discovery_Scanner")

DISCOVERY_CACHE = {}
CACHE_TTL = 0  # Temporarily disable discovery cache for real-time results as per instructions


class AWSDiscoveryScanner:

    @staticmethod
    def scan_all(
        region: str = None
    ) -> ScanResult:

        now = time.time()
        started_at = datetime.utcnow()
        scan_id = str(uuid.uuid4())
        cache_key = region or "all_regions"
        if CACHE_TTL > 0 and cache_key in DISCOVERY_CACHE:
            cached_data, timestamp = DISCOVERY_CACHE[cache_key]
            if now - timestamp < CACHE_TTL:
                logger.info(f"[DISCOVERY CACHE] HIT for region: {cache_key}")
                return cached_data

        logger.info(f"[DISCOVERY CACHE] MISS for region: {cache_key}")
        resources = []

        if region and region.strip().lower() != "all":
            regions_to_scan = [region.strip()]
        else:
            regions_to_scan = [r for r in get_all_regions() if r.lower() != "all"]

        logger.info(f"Scanning regions: {regions_to_scan}")

        for reg in regions_to_scan:
            logger.info(f"Starting scan for region: {reg}")

            # EC2
            try:
                for inst in EC2Discovery.discover(reg):
                    deps = []
                    if inst.get("vpc_id"):
                        deps.append({"type": "VPC", "id": inst["vpc_id"], "name": inst["vpc_id"]})
                    if inst.get("subnet_id"):
                        deps.append({"type": "Subnet", "id": inst["subnet_id"], "name": inst["subnet_id"]})
                    for sg in inst.get("security_groups", []):
                        deps.append({"type": "SecurityGroup", "id": sg, "name": sg})
                    for vol_id in inst.get("ebs_volumes", []):
                        deps.append({"type": "EBS", "id": vol_id, "name": vol_id})
                    if inst.get("iam_instance_profile"):
                        arn = inst["iam_instance_profile"]
                        name = arn.split("/")[-1] if "/" in arn else arn
                        deps.append({"type": "IAM", "id": arn, "name": name})

                    resources.append({
                        "provider": "AWS",
                        "resource_id": inst["resource_id"],
                        "resource_type": "EC2",
                        "name": inst["resource_id"],
                        "status": inst["state"],
                        "region": reg,
                        "metadata": {
                            "instance_type": inst.get("instance_type"),
                            "launch_time": inst.get("launch_time"),
                        },
                        "dependencies": deps
                    })

            except Exception as e:
                logger.warning(
                    f"EC2 Discovery failed in region {reg}: {e}"
                )

            # RDS
            try:
                for db in RDSDiscovery.discover(reg):
                    deps = []
                    subnet_group = db.get("subnet_group", {})
                    if subnet_group:
                        vpc_id = subnet_group.get("VpcId")
                        if vpc_id:
                            deps.append({"type": "VPC", "id": vpc_id, "name": vpc_id})
                        for sub in subnet_group.get("Subnets", []):
                            sub_id = sub.get("SubnetIdentifier")
                            if sub_id:
                                deps.append({"type": "Subnet", "id": sub_id, "name": sub_id})
                    for sg in db.get("vpc_security_groups", []):
                        sg_id = sg.get("VpcSecurityGroupId")
                        if sg_id:
                            deps.append({"type": "SecurityGroup", "id": sg_id, "name": sg_id})

                    resources.append({
                        "provider": "AWS",
                        "resource_id": db["resource_id"],
                        "resource_type": "RDS",
                        "name": db["resource_id"],
                        "status": db["status"],
                        "region": reg,
                        "metadata": {
                            "instance_class": db.get("class"),
                            "engine": db.get("engine"),
                        },
                        "dependencies": deps
                    })

            except Exception as e:
                logger.warning(
                    f"RDS Discovery failed in region {reg}: {e}"
                )

            # Lambda
            try:
                for fn in LambdaDiscovery.discover(reg):
                    deps = []
                    role_arn = fn.get("role")
                    if role_arn:
                        deps.append({"type": "IAM", "id": role_arn, "name": role_arn})
                    vpc_config = fn.get("vpc_config", {})
                    if vpc_config:
                        vpc_id = vpc_config.get("VpcId")
                        if vpc_id:
                            deps.append({"type": "VPC", "id": vpc_id, "name": vpc_id})
                        for sub in vpc_config.get("SubnetIds", []):
                            deps.append({"type": "Subnet", "id": sub, "name": sub})
                        for sg in vpc_config.get("SecurityGroupIds", []):
                            deps.append({"type": "SecurityGroup", "id": sg, "name": sg})

                    resources.append({
                        "provider": "AWS",
                        "resource_id": fn["resource_id"],
                        "resource_type": "Lambda",
                        "name": fn["resource_id"],
                        "status": "active",
                        "region": reg,
                        "metadata": {
                            "memory_size": fn.get("memory_size"),
                            "runtime": fn.get("runtime"),
                        },
                        "dependencies": deps
                    })

            except Exception as e:
                logger.warning(
                    f"Lambda Discovery failed in region {reg}: {e}"
                )

            # VPC
            try:
                for vpc in VPCDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": vpc["resource_id"],
                        "resource_type": "VPC",
                        "name": vpc["resource_id"],
                        "status": vpc.get("state", "available"),
                        "region": reg,
                        "metadata": {},
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"VPC Discovery failed in region {reg}: {e}")

            # Subnet
            try:
                for subnet in SubnetDiscovery.discover(reg):
                    deps = []
                    if subnet.get("vpc_id"):
                        deps.append({"type": "VPC", "id": subnet["vpc_id"], "name": subnet["vpc_id"]})
                    resources.append({
                        "provider": "AWS",
                        "resource_id": subnet["resource_id"],
                        "resource_type": "Subnet",
                        "name": subnet["resource_id"],
                        "status": subnet.get("state", "available"),
                        "region": reg,
                        "metadata": {
                            "availability_zone": subnet.get("availability_zone"),
                            "cidr_block": subnet.get("cidr_block"),
                        },
                        "dependencies": deps
                    })
            except Exception as e:
                logger.warning(f"Subnet Discovery failed in region {reg}: {e}")

            # Security Group
            try:
                for sg in SecurityGroupDiscovery.discover(reg):
                    deps = []
                    if sg.get("vpc_id"):
                        deps.append({"type": "VPC", "id": sg["vpc_id"], "name": sg["vpc_id"]})
                    resources.append({
                        "provider": "AWS",
                        "resource_id": sg["resource_id"],
                        "resource_type": "SecurityGroup",
                        "name": sg.get("name", sg["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "metadata": {
                            "ingress_rules": sg.get("ingress_rules"),
                            "egress_rules": sg.get("egress_rules"),
                            "description": sg.get("description"),
                        },
                        "dependencies": deps
                    })
            except Exception as e:
                logger.warning(f"Security Group Discovery failed in region {reg}: {e}")

            # Route Table
            try:
                for rt in RouteTableDiscovery.discover(reg):
                    deps = []
                    if rt.get("vpc_id"):
                        deps.append({"type": "VPC", "id": rt["vpc_id"], "name": rt["vpc_id"]})
                    for sub in rt.get("subnets", []):
                        deps.append({"type": "Subnet", "id": sub, "name": sub})
                    for igw in rt.get("internet_gateways", []):
                        deps.append({"type": "InternetGateway", "id": igw, "name": igw})
                    for nat in rt.get("nat_gateways", []):
                        deps.append({"type": "NatGateway", "id": nat, "name": nat})
                    resources.append({
                        "provider": "AWS",
                        "resource_id": rt["resource_id"],
                        "resource_type": "RouteTable",
                        "name": rt["resource_id"],
                        "status": "active",
                        "region": reg,
                        "metadata": {
                            "route_count": rt.get("route_count"),
                        },
                        "dependencies": deps
                    })
            except Exception as e:
                logger.warning(f"Route Table Discovery failed in region {reg}: {e}")

            # NAT Gateway
            try:
                for nat in NatGatewayDiscovery.discover(reg):
                    deps = []
                    if nat.get("vpc_id"):
                        deps.append({"type": "VPC", "id": nat["vpc_id"], "name": nat["vpc_id"]})
                    if nat.get("subnet_id"):
                        deps.append({"type": "Subnet", "id": nat["subnet_id"], "name": nat["subnet_id"]})
                    resources.append({
                        "provider": "AWS",
                        "resource_id": nat["resource_id"],
                        "resource_type": "NatGateway",
                        "name": nat["resource_id"],
                        "status": nat.get("state", "available"),
                        "region": reg,
                        "metadata": {
                            "connectivity_type": nat.get("connectivity_type"),
                        },
                        "dependencies": deps
                    })
            except Exception as e:
                logger.warning(f"NAT Gateway Discovery failed in region {reg}: {e}")

            # Network Interface (ENI)
            try:
                for eni in NetworkInterfaceDiscovery.discover(reg):
                    deps = []
                    if eni.get("vpc_id"):
                        deps.append({"type": "VPC", "id": eni["vpc_id"], "name": eni["vpc_id"]})
                    if eni.get("subnet_id"):
                        deps.append({"type": "Subnet", "id": eni["subnet_id"], "name": eni["subnet_id"]})
                    for sg in eni.get("security_groups", []):
                        deps.append({"type": "SecurityGroup", "id": sg, "name": sg})
                    resources.append({
                        "provider": "AWS",
                        "resource_id": eni["resource_id"],
                        "resource_type": "NetworkInterface",
                        "name": eni["resource_id"],
                        "status": eni.get("status", "available"),
                        "region": reg,
                        "metadata": {
                            "interface_type": eni.get("interface_type"),
                            "private_ip": eni.get("private_ip"),
                        },
                        "dependencies": deps
                    })
            except Exception as e:
                logger.warning(f"Network Interface Discovery failed in region {reg}: {e}")

            # Elastic IP
            try:
                for eip in ElasticIPDiscovery.discover(reg):
                    deps = []
                    if eip.get("network_interface_id"):
                        deps.append({"type": "NetworkInterface", "id": eip["network_interface_id"], "name": eip["network_interface_id"]})
                    resources.append({
                        "provider": "AWS",
                        "resource_id": eip["resource_id"],
                        "resource_type": "ElasticIP",
                        "name": eip.get("public_ip", eip["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "metadata": {
                            "public_ip": eip.get("public_ip"),
                        },
                        "dependencies": deps
                    })
            except Exception as e:
                logger.warning(f"Elastic IP Discovery failed in region {reg}: {e}")

            # IGW
            try:
                for igw in IGWDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": igw["resource_id"],
                        "resource_type": "InternetGateway",
                        "name": igw["resource_id"],
                        "status": igw.get("state", "available"),
                        "region": reg,
                        "metadata": {},
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"IGW Discovery failed in region {reg}: {e}")

            # ALB
            try:
                for alb in ALBDiscovery.discover(reg):
                    deps = []
                    if alb.get("vpc_id"):
                        deps.append({"type": "VPC", "id": alb["vpc_id"], "name": alb["vpc_id"]})
                    for sub in alb.get("subnets", []):
                        deps.append({"type": "Subnet", "id": sub, "name": sub})
                    for sg in alb.get("security_groups", []):
                        deps.append({"type": "SecurityGroup", "id": sg, "name": sg})
                    resources.append({
                        "provider": "AWS",
                        "resource_id": alb["resource_id"],
                        "resource_type": alb.get("resource_type", "ALB"),
                        "name": alb.get("name", alb["resource_id"]),
                        "status": alb.get("state", "active"),
                        "region": reg,
                        "metadata": {
                            "scheme": alb.get("scheme"),
                            "dns_name": alb.get("dns_name"),
                        },
                        "dependencies": deps
                    })

            except Exception as e:
                logger.warning(
                    f"ALB Discovery failed in region {reg}: {e}"
                )

            # EBS
            try:
                for vol in EBSDiscovery.discover(reg):

                    resources.append({
                        "provider": "AWS",
                        "resource_id": vol["resource_id"],
                        "resource_type": "EBS",
                        "name": vol["resource_id"],
                        "status": vol["state"],
                        "region": reg,
                        "metadata": {
                            "size_gb": vol.get("size_gb"),
                        },
                        "dependencies": []
                    })

            except Exception as e:
                logger.warning(
                    f"EBS Discovery failed in region {reg}: {e}"
                )

            # ECS
            try:
                for ecs in ECSDiscovery.discover(reg):

                    resources.append({
                        "provider": "AWS",
                        "resource_id": ecs["resource_id"],
                        "resource_type": "ECS",
                        "name": ecs["resource_id"],
                        "status": "active",
                        "region": reg,
                        "metadata": {},
                        "dependencies": []
                    })

            except Exception as e:
                logger.warning(
                    f"ECS Discovery failed in region {reg}: {e}"
                )

            # EKS
            try:
                for eks in EKSDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": eks["resource_id"],
                        "resource_type": "EKS",
                        "name": eks["resource_id"],
                        "status": "active",
                        "region": reg,
                        "metadata": {},
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"EKS Discovery failed in region {reg}: {e}")

            # Auto Scaling Group
            try:
                for asg in AutoScalingDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": asg["resource_id"],
                        "resource_type": "AutoScalingGroup",
                        "name": asg.get("name", asg["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "metadata": {
                            "min_size": asg.get("min_size"),
                            "max_size": asg.get("max_size"),
                            "desired_capacity": asg.get("desired_capacity"),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"Auto Scaling Discovery failed in region {reg}: {e}")

            # Target Group
            try:
                for tg in TargetGroupDiscovery.discover(reg):
                    deps = []
                    if tg.get("vpc_id"):
                        deps.append({"type": "VPC", "id": tg["vpc_id"], "name": tg["vpc_id"]})
                    for lb in tg.get("load_balancers", []):
                        deps.append({"type": "ALB", "id": lb, "name": lb})
                    resources.append({
                        "provider": "AWS",
                        "resource_id": tg["resource_id"],
                        "resource_type": "TargetGroup",
                        "name": tg.get("name", tg["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "metadata": {
                            "protocol": tg.get("protocol"),
                            "port": tg.get("port"),
                            "target_type": tg.get("target_type"),
                        },
                        "dependencies": deps
                    })
            except Exception as e:
                logger.warning(f"Target Group Discovery failed in region {reg}: {e}")

            # ── Phase 4 Regional Providers ───────────────────────────────────

            # API Gateway (REST + HTTP)
            try:
                for apigw in APIGatewayDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": apigw["resource_id"],
                        "resource_type": apigw["resource_type"],
                        "name": apigw.get("name", apigw["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "metadata": {
                            "protocol": apigw.get("protocol"),
                            "endpoint": apigw.get("endpoint"),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"API Gateway Discovery failed in region {reg}: {e}")

            # WAF Web ACLs (Regional)
            try:
                for acl in WAFDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": acl["resource_id"],
                        "resource_type": acl["resource_type"],
                        "name": acl.get("name", acl["resource_id"]),
                        "status": "active",
                        "region": acl.get("region", reg),
                        "metadata": {
                            "rule_count": acl.get("rule_count", 0),
                            "scope": acl.get("scope"),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"WAF Discovery failed in region {reg}: {e}")

            # Secrets Manager
            try:
                for secret in SecretsManagerDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": secret["resource_id"],
                        "resource_type": secret["resource_type"],
                        "name": secret.get("name", secret["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "metadata": {
                            "rotation_enabled": secret.get("rotation_enabled"),
                            "kms_key_id": secret.get("kms_key_id"),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"Secrets Manager Discovery failed in region {reg}: {e}")

            # SSM Parameter Store
            try:
                for param in SSMDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": param["resource_id"],
                        "resource_type": param["resource_type"],
                        "name": param.get("name", param["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "metadata": {
                            "type": param.get("type"),
                            "tier": param.get("tier"),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"SSM Discovery failed in region {reg}: {e}")

            # SNS Topics
            try:
                for topic in SNSDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": topic["resource_id"],
                        "resource_type": topic["resource_type"],
                        "name": topic.get("name", topic["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "metadata": {
                            "subscription_count": topic.get("subscription_count", 0),
                            "fifo": topic.get("fifo", False),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"SNS Discovery failed in region {reg}: {e}")

            # SQS Queues
            try:
                for queue in SQSDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": queue["resource_id"],
                        "resource_type": queue["resource_type"],
                        "name": queue.get("name", queue["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "metadata": {
                            "fifo": queue.get("is_fifo"),
                            "dlq": queue.get("dlq_arn"),
                            "approximate_messages": queue.get("approximate_messages", 0),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"SQS Discovery failed in region {reg}: {e}")

            # EventBridge Buses + Rules
            try:
                for eb in EventBridgeDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": eb["resource_id"],
                        "resource_type": eb["resource_type"],
                        "name": eb.get("name", eb["resource_id"]),
                        "status": eb.get("state", "active"),
                        "region": reg,
                        "metadata": {
                            "state": eb.get("state"),
                            "targets": eb.get("targets", []),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"EventBridge Discovery failed in region {reg}: {e}")

            # DynamoDB Tables
            try:
                for table in DynamoDBDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": table["resource_id"],
                        "resource_type": table["resource_type"],
                        "name": table.get("name", table["resource_id"]),
                        "status": table.get("status", "active"),
                        "region": reg,
                        "metadata": {
                            "billing_mode": table.get("billing_mode"),
                            "item_count": table.get("item_count", 0),
                            "encryption_status": table.get("encryption_status"),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"DynamoDB Discovery failed in region {reg}: {e}")

            # ElastiCache
            try:
                for ec_res in ElastiCacheDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": ec_res["resource_id"],
                        "resource_type": ec_res["resource_type"],
                        "name": ec_res.get("name", ec_res["resource_id"]),
                        "status": ec_res.get("status", "active"),
                        "region": reg,
                        "metadata": {
                            "engine": ec_res.get("engine"),
                            "node_type": ec_res.get("node_type"),
                            "multi_az": ec_res.get("multi_az"),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"ElastiCache Discovery failed in region {reg}: {e}")

            # OpenSearch Domains
            try:
                for domain in OpenSearchDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": domain["resource_id"],
                        "resource_type": domain["resource_type"],
                        "name": domain.get("name", domain["resource_id"]),
                        "status": domain.get("status", "active"),
                        "region": reg,
                        "metadata": {
                            "engine_version": domain.get("engine_version"),
                            "instance_type": domain.get("instance_type"),
                            "encryption_at_rest": domain.get("encryption_at_rest"),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"OpenSearch Discovery failed in region {reg}: {e}")

            # EFS File Systems + Mount Targets
            try:
                for efs_res in EFSDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "resource_id": efs_res["resource_id"],
                        "resource_type": efs_res["resource_type"],
                        "name": efs_res.get("name", efs_res["resource_id"]),
                        "status": efs_res.get("lifecycle_state", "active"),
                        "region": reg,
                        "metadata": {
                            "throughput_mode": efs_res.get("throughput_mode"),
                            "encrypted": efs_res.get("encrypted"),
                        },
                        "dependencies": []
                    })
            except Exception as e:
                logger.warning(f"EFS Discovery failed in region {reg}: {e}")

        try:
            for bucket in S3Discovery.discover():

                resources.append({
                    "provider": "AWS",
                    "resource_id": bucket["resource_id"],
                    "resource_type": "S3",
                    "name": bucket["resource_id"],
                    "status": "active",
                    "region": "global",
                    "metadata": {
                        "size_gb": 0,
                        "created": bucket.get("created"),
                    },
                    "dependencies": []
                })

        except Exception as e:
            logger.warning(
                f"S3 Discovery failed: {e}"
            )

        # IAM (Global)
        try:
            for user in IAMDiscovery.discover():

                resources.append({
                    "provider": "AWS",
                    "resource_id": user["resource_id"],
                    "resource_type": "IAM",
                    "name": user["resource_id"],
                    "status": "active",
                    "region": "global",
                    "metadata": {},
                    "dependencies": []
                })

        except Exception as e:
            logger.warning(
                f"IAM Discovery failed: {e}"
            )

        # ── Phase 4 Global Providers ─────────────────────────────────────────

        # CloudFront (global)
        try:
            for dist in CloudFrontDiscovery.discover():
                deps = []
                if dist.get("web_acl_id"):
                    deps.append({"type": "WAF", "id": dist["web_acl_id"], "name": dist["web_acl_id"]})
                resources.append({
                    "provider": "AWS",
                    "resource_id": dist["resource_id"],
                    "resource_type": dist["resource_type"],
                    "name": dist.get("name", dist["resource_id"]),
                    "status": dist.get("status", "active"),
                    "region": "global",
                    "metadata": {
                        "domain_name": dist.get("domain_name"),
                        "waf": bool(dist.get("web_acl_id")),
                    },
                    "dependencies": deps
                })
        except Exception as e:
            logger.warning(f"CloudFront Discovery failed: {e}")

        # Route 53 (global)
        try:
            for r53 in Route53Discovery.discover():
                resources.append({
                    "provider": "AWS",
                    "resource_id": r53["resource_id"],
                    "resource_type": r53["resource_type"],
                    "name": r53.get("name", r53["resource_id"]),
                    "status": "active",
                    "region": "global",
                    "metadata": {
                        "record_type": r53.get("record_type"),
                        "is_alias": r53.get("is_alias", False),
                    },
                    "dependencies": []
                })
        except Exception as e:
            logger.warning(f"Route53 Discovery failed: {e}")

        finished_at = datetime.utcnow()
        duration = int((finished_at - started_at).total_seconds())

        scan_result = ScanResult(
            scan_id=scan_id,
            account_id=None,
            regions=regions_to_scan,
            started_at=started_at,
            finished_at=finished_at,
            duration=duration,
            resources=resources,
            warnings=[],
            errors=[],
            statistics={"total_resources": len(resources)}
        )

        DISCOVERY_CACHE[cache_key] = (scan_result, now)
        return scan_result
