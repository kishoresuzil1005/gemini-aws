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

        if region:
            regions_to_scan = [region]
        else:
            regions_to_scan = get_all_regions()

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
                        "id": inst["resource_id"],
                        "type": "EC2",
                        "name": inst["resource_id"],
                        "status": inst["state"],
                        "region": reg,
                        "instance_type": inst.get("instance_type"),
                        "configuration_hint": f"Type={inst.get('instance_type')} Launch={inst.get('launch_time')}",
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
                        "id": db["resource_id"],
                        "type": "RDS",
                        "name": db["resource_id"],
                        "status": db["status"],
                        "region": reg,
                        "instance_class": db.get("class"),
                        "configuration_hint": f"Engine={db.get('engine')} Class={db.get('class')}",
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
                        "id": fn["resource_id"],
                        "type": "Lambda",
                        "name": fn["resource_id"],
                        "status": "active",
                        "region": reg,
                        "memory_size": fn.get("memory_size"),
                        "configuration_hint": f"Runtime={fn.get('runtime')} Memory={fn.get('memory_size')}MB",
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
                        "id": vpc["resource_id"],
                        "type": "VPC",
                        "name": vpc["resource_id"],
                        "status": vpc.get("state", "available"),
                        "region": reg
                    })
            except Exception as e:
                logger.warning(f"VPC Discovery failed in region {reg}: {e}")

            # Subnet
            try:
                for subnet in SubnetDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": subnet["resource_id"],
                        "type": "Subnet",
                        "name": subnet["resource_id"],
                        "status": subnet.get("state", "available"),
                        "region": reg,
                        "configuration_hint": f"AZ={subnet.get('availability_zone')} CIDR={subnet.get('cidr_block')}"
                    })
            except Exception as e:
                logger.warning(f"Subnet Discovery failed in region {reg}: {e}")

            # Security Group
            try:
                for sg in SecurityGroupDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": sg["resource_id"],
                        "type": "SecurityGroup",
                        "name": sg.get("name", sg["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "configuration_hint": f"Ingress={sg.get('ingress_rules')} Egress={sg.get('egress_rules')}"
                    })
            except Exception as e:
                logger.warning(f"Security Group Discovery failed in region {reg}: {e}")

            # Route Table
            try:
                for rt in RouteTableDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": rt["resource_id"],
                        "type": "RouteTable",
                        "name": rt["resource_id"],
                        "status": "active",
                        "region": reg,
                        "configuration_hint": f"Routes={rt.get('route_count')}"
                    })
            except Exception as e:
                logger.warning(f"Route Table Discovery failed in region {reg}: {e}")

            # NAT Gateway
            try:
                for nat in NatGatewayDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": nat["resource_id"],
                        "type": "NatGateway",
                        "name": nat["resource_id"],
                        "status": nat.get("state", "available"),
                        "region": reg,
                        "configuration_hint": f"Type={nat.get('connectivity_type')}"
                    })
            except Exception as e:
                logger.warning(f"NAT Gateway Discovery failed in region {reg}: {e}")

            # Network Interface (ENI)
            try:
                for eni in NetworkInterfaceDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": eni["resource_id"],
                        "type": "NetworkInterface",
                        "name": eni["resource_id"],
                        "status": eni.get("status", "available"),
                        "region": reg,
                        "configuration_hint": f"Type={eni.get('interface_type')} IP={eni.get('private_ip')}"
                    })
            except Exception as e:
                logger.warning(f"Network Interface Discovery failed in region {reg}: {e}")

            # Elastic IP
            try:
                for eip in ElasticIPDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": eip["resource_id"],
                        "type": "ElasticIP",
                        "name": eip.get("public_ip", eip["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "configuration_hint": f"PublicIP={eip.get('public_ip')}"
                    })
            except Exception as e:
                logger.warning(f"Elastic IP Discovery failed in region {reg}: {e}")

            # IGW
            try:
                for igw in IGWDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": igw["resource_id"],
                        "type": "InternetGateway",
                        "name": igw["resource_id"],
                        "status": igw.get("state", "available"),
                        "region": reg
                    })
            except Exception as e:
                logger.warning(f"IGW Discovery failed in region {reg}: {e}")

            # ALB
            try:
                for alb in ALBDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": alb["resource_id"],
                        "type": alb.get("resource_type", "ALB"),
                        "name": alb.get("name", alb["resource_id"]),
                        "status":
                            alb.get("state", "active"),
                        "region": reg
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
                        "id": vol["resource_id"],
                        "type": "EBS",
                        "name": vol["resource_id"],
                        "status": vol["state"],
                        "region": reg,

                        "size_gb":
                            vol.get("size_gb"),

                        "configuration_hint":
                            f"Size={vol.get('size_gb')}GB"
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
                        "id": ecs["resource_id"],
                        "type": "ECS",
                        "name": ecs["resource_id"],
                        "status": "active",
                        "region": reg
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
                        "id": eks["resource_id"],
                        "type": "EKS",
                        "name": eks["resource_id"],
                        "status": "active",
                        "region": reg
                    })
            except Exception as e:
                logger.warning(f"EKS Discovery failed in region {reg}: {e}")

            # Auto Scaling Group
            try:
                for asg in AutoScalingDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": asg["resource_id"],
                        "type": "AutoScalingGroup",
                        "name": asg.get("name", asg["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "configuration_hint": f"Min={asg.get('min_size')} Max={asg.get('max_size')} Desired={asg.get('desired_capacity')}"
                    })
            except Exception as e:
                logger.warning(f"Auto Scaling Discovery failed in region {reg}: {e}")

            # Target Group
            try:
                for tg in TargetGroupDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": tg["resource_id"],
                        "type": "TargetGroup",
                        "name": tg.get("name", tg["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "configuration_hint": f"Protocol={tg.get('protocol')} Port={tg.get('port')} Type={tg.get('target_type')}"
                    })
            except Exception as e:
                logger.warning(f"Target Group Discovery failed in region {reg}: {e}")

            # ── Phase 4 Regional Providers ───────────────────────────────────

            # API Gateway (REST + HTTP)
            try:
                for apigw in APIGatewayDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": apigw["resource_id"],
                        "type": apigw["resource_type"],
                        "name": apigw.get("name", apigw["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "configuration_hint": f"Protocol={apigw.get('protocol')} Endpoint={apigw.get('endpoint', '')[:80]}"
                    })
            except Exception as e:
                logger.warning(f"API Gateway Discovery failed in region {reg}: {e}")

            # WAF Web ACLs (Regional)
            try:
                for acl in WAFDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": acl["resource_id"],
                        "type": acl["resource_type"],
                        "name": acl.get("name", acl["resource_id"]),
                        "status": "active",
                        "region": acl.get("region", reg),
                        "configuration_hint": f"Rules={acl.get('rule_count', 0)} Scope={acl.get('scope')}"
                    })
            except Exception as e:
                logger.warning(f"WAF Discovery failed in region {reg}: {e}")

            # Secrets Manager
            try:
                for secret in SecretsManagerDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": secret["resource_id"],
                        "type": secret["resource_type"],
                        "name": secret.get("name", secret["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "configuration_hint": f"Rotation={secret.get('rotation_enabled')} KMS={bool(secret.get('kms_key_id'))}"
                    })
            except Exception as e:
                logger.warning(f"Secrets Manager Discovery failed in region {reg}: {e}")

            # SSM Parameter Store
            try:
                for param in SSMDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": param["resource_id"],
                        "type": param["resource_type"],
                        "name": param.get("name", param["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "configuration_hint": f"Type={param.get('type')} Tier={param.get('tier')}"
                    })
            except Exception as e:
                logger.warning(f"SSM Discovery failed in region {reg}: {e}")

            # SNS Topics
            try:
                for topic in SNSDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": topic["resource_id"],
                        "type": topic["resource_type"],
                        "name": topic.get("name", topic["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "configuration_hint": f"Subscriptions={topic.get('subscription_count', 0)} FIFO={topic.get('fifo', False)}"
                    })
            except Exception as e:
                logger.warning(f"SNS Discovery failed in region {reg}: {e}")

            # SQS Queues
            try:
                for queue in SQSDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": queue["resource_id"],
                        "type": queue["resource_type"],
                        "name": queue.get("name", queue["resource_id"]),
                        "status": "active",
                        "region": reg,
                        "configuration_hint": f"FIFO={queue.get('is_fifo')} DLQ={bool(queue.get('dlq_arn'))} Messages={queue.get('approximate_messages', 0)}"
                    })
            except Exception as e:
                logger.warning(f"SQS Discovery failed in region {reg}: {e}")

            # EventBridge Buses + Rules
            try:
                for eb in EventBridgeDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": eb["resource_id"],
                        "type": eb["resource_type"],
                        "name": eb.get("name", eb["resource_id"]),
                        "status": eb.get("state", "active"),
                        "region": reg,
                        "configuration_hint": f"State={eb.get('state')} Targets={len(eb.get('targets', []))}"
                    })
            except Exception as e:
                logger.warning(f"EventBridge Discovery failed in region {reg}: {e}")

            # DynamoDB Tables
            try:
                for table in DynamoDBDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": table["resource_id"],
                        "type": table["resource_type"],
                        "name": table.get("name", table["resource_id"]),
                        "status": table.get("status", "active"),
                        "region": reg,
                        "configuration_hint": f"Billing={table.get('billing_mode')} Items={table.get('item_count', 0)} Encrypted={table.get('encryption_status')}"
                    })
            except Exception as e:
                logger.warning(f"DynamoDB Discovery failed in region {reg}: {e}")

            # ElastiCache
            try:
                for ec_res in ElastiCacheDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": ec_res["resource_id"],
                        "type": ec_res["resource_type"],
                        "name": ec_res.get("name", ec_res["resource_id"]),
                        "status": ec_res.get("status", "active"),
                        "region": reg,
                        "configuration_hint": f"Engine={ec_res.get('engine')} NodeType={ec_res.get('node_type')} MultiAZ={ec_res.get('multi_az')}"
                    })
            except Exception as e:
                logger.warning(f"ElastiCache Discovery failed in region {reg}: {e}")

            # OpenSearch Domains
            try:
                for domain in OpenSearchDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": domain["resource_id"],
                        "type": domain["resource_type"],
                        "name": domain.get("name", domain["resource_id"]),
                        "status": domain.get("status", "active"),
                        "region": reg,
                        "configuration_hint": f"Engine={domain.get('engine_version')} Instance={domain.get('instance_type')} Encrypted={domain.get('encryption_at_rest')}"
                    })
            except Exception as e:
                logger.warning(f"OpenSearch Discovery failed in region {reg}: {e}")

            # EFS File Systems + Mount Targets
            try:
                for efs_res in EFSDiscovery.discover(reg):
                    resources.append({
                        "provider": "AWS",
                        "id": efs_res["resource_id"],
                        "type": efs_res["resource_type"],
                        "name": efs_res.get("name", efs_res["resource_id"]),
                        "status": efs_res.get("lifecycle_state", "active"),
                        "region": reg,
                        "configuration_hint": f"Throughput={efs_res.get('throughput_mode')} Encrypted={efs_res.get('encrypted')}"
                    })
            except Exception as e:
                logger.warning(f"EFS Discovery failed in region {reg}: {e}")

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

        # IAM (Global)
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

        # ── Phase 4 Global Providers ─────────────────────────────────────────

        # CloudFront (global)
        try:
            for dist in CloudFrontDiscovery.discover():
                resources.append({
                    "provider": "AWS",
                    "id": dist["resource_id"],
                    "type": dist["resource_type"],
                    "name": dist.get("name", dist["resource_id"]),
                    "status": dist.get("status", "active"),
                    "region": "global",
                    "configuration_hint": f"Domain={dist.get('domain_name')} WAF={bool(dist.get('web_acl_id'))}"
                })
        except Exception as e:
            logger.warning(f"CloudFront Discovery failed: {e}")

        # Route 53 (global)
        try:
            for r53 in Route53Discovery.discover():
                resources.append({
                    "provider": "AWS",
                    "id": r53["resource_id"],
                    "type": r53["resource_type"],
                    "name": r53.get("name", r53["resource_id"]),
                    "status": "active",
                    "region": "global",
                    "configuration_hint": f"Type={r53.get('record_type', '')} Alias={r53.get('is_alias', False)}"
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
