import re

providers = [
    ("EC2Discovery", True), ("RDSDiscovery", True), ("LambdaDiscovery", True),
    ("VPCDiscovery", True), ("ALBDiscovery", True), ("EBSDiscovery", True),
    ("ECSDiscovery", True), ("EKSDiscovery", True), ("IGWDiscovery", True),
    ("SubnetDiscovery", True), ("SecurityGroupDiscovery", True),
    ("RouteTableDiscovery", True), ("NatGatewayDiscovery", True),
    ("NetworkInterfaceDiscovery", True), ("ElasticIPDiscovery", True),
    ("AutoScalingDiscovery", True), ("TargetGroupDiscovery", True),
    ("APIGatewayDiscovery", True), ("WAFDiscovery", True),
    ("SecretsManagerDiscovery", True), ("SSMDiscovery", True),
    ("SNSDiscovery", True), ("SQSDiscovery", True),
    ("EventBridgeDiscovery", True), ("DynamoDBDiscovery", True),
    ("ElastiCacheDiscovery", True), ("OpenSearchDiscovery", True),
    ("EFSDiscovery", True), 
    ("S3Discovery", False), ("IAMDiscovery", False), 
    ("CloudFrontDiscovery", False), ("Route53Discovery", False)
]

code = """import logging
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
from app.providers.aws.subnet import SubnetDiscovery
from app.providers.aws.security_group import SecurityGroupDiscovery
from app.providers.aws.route_table import RouteTableDiscovery
from app.providers.aws.nat_gateway import NatGatewayDiscovery
from app.providers.aws.network_interface import NetworkInterfaceDiscovery
from app.providers.aws.elastic_ip import ElasticIPDiscovery
from app.providers.aws.autoscaling import AutoScalingDiscovery
from app.providers.aws.target_group import TargetGroupDiscovery
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
CACHE_TTL = 0

class AWSDiscoveryScanner:

    @staticmethod
    def scan_all(region: str = None) -> ScanResult:
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
"""

for provider, is_regional in providers:
    if is_regional:
        code += f"""
            try:
                resources.extend({provider}.discover(reg))
            except Exception as e:
                logger.warning(f"{provider} failed in region {{reg}}: {{e}}")
"""

code += """
        # Global providers
"""

for provider, is_regional in providers:
    if not is_regional:
        code += f"""
        try:
            resources.extend({provider}.discover())
        except Exception as e:
            logger.warning(f"{provider} failed: {{e}}")
"""

code += """
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
"""

with open("backend/app/services/discovery/scanner.py", "w") as f:
    f.write(code)

