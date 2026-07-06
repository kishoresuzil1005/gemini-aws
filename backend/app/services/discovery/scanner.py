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

            try:
                resources.extend(EC2Discovery.discover(reg))
            except Exception as e:
                logger.warning(f"EC2Discovery failed in region {reg}: {e}")

            try:
                resources.extend(RDSDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"RDSDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(LambdaDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"LambdaDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(VPCDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"VPCDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(ALBDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"ALBDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(EBSDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"EBSDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(ECSDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"ECSDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(EKSDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"EKSDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(IGWDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"IGWDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(SubnetDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"SubnetDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(SecurityGroupDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"SecurityGroupDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(RouteTableDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"RouteTableDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(NatGatewayDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"NatGatewayDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(NetworkInterfaceDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"NetworkInterfaceDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(ElasticIPDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"ElasticIPDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(AutoScalingDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"AutoScalingDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(TargetGroupDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"TargetGroupDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(APIGatewayDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"APIGatewayDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(WAFDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"WAFDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(SecretsManagerDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"SecretsManagerDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(SSMDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"SSMDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(SNSDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"SNSDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(SQSDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"SQSDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(EventBridgeDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"EventBridgeDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(DynamoDBDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"DynamoDBDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(ElastiCacheDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"ElastiCacheDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(OpenSearchDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"OpenSearchDiscovery failed in region {reg}: {e}")

            try:
                resources.extend(EFSDiscovery.discover(reg))
            except Exception as e:
                logger.warning(f"EFSDiscovery failed in region {reg}: {e}")

        # Global providers

        try:
            resources.extend(S3Discovery.discover())
        except Exception as e:
            logger.warning(f"S3Discovery failed: {e}")

        try:
            resources.extend(IAMDiscovery.discover())
        except Exception as e:
            logger.warning(f"IAMDiscovery failed: {e}")

        try:
            resources.extend(CloudFrontDiscovery.discover())
        except Exception as e:
            logger.warning(f"CloudFrontDiscovery failed: {e}")

        try:
            resources.extend(Route53Discovery.discover())
        except Exception as e:
            logger.warning(f"Route53Discovery failed: {e}")

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
