from app.core.logging import get_logger
logger = get_logger(__name__)
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
                logger.debug("EC2 START")
                resources.extend(EC2Discovery.discover(reg))
                logger.debug("EC2 DONE")
            except Exception as e:
                logger.warning(f"EC2Discovery failed in region {reg}: {e}")

            try:
                logger.debug("RDS START")
                resources.extend(RDSDiscovery.discover(reg))
                logger.debug("RDS DONE")
            except Exception as e:
                logger.warning(f"RDSDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("LAMBDA START")
                lambda_resources = LambdaDiscovery.discover(reg)
                logger.debug("=" * 80)
                logger.debug(f"LAMBDA DISCOVERED: {len(lambda_resources)}")
                for r in lambda_resources:
                    logger.debug(f"RESOURCE: {r.get("resource_id", "UNKNOWN")}")
                    logger.debug(f"DEPENDENCIES: {r.get("dependencies")}")
                    logger.debug(f"CONFIGURATION: {r.get("configuration")}")
                logger.debug("=" * 80)
                resources.extend(lambda_resources)
                logger.debug("LAMBDA DONE")
            except Exception as e:
                logger.warning(f"LambdaDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("VPC START")
                resources.extend(VPCDiscovery.discover(reg))
                logger.debug("VPC DONE")
            except Exception as e:
                logger.warning(f"VPCDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("ALB START")
                alb_resources = ALBDiscovery.discover(reg)
                logger.debug("=" * 80)
                logger.debug(f"ALB DISCOVERED: {len(alb_resources)}")
                for r in alb_resources:
                    logger.debug(f"RESOURCE: {r.get("resource_id", "UNKNOWN")}")
                    logger.debug(f"DEPENDENCIES: {r.get("dependencies")}")
                    logger.debug(f"METADATA: {r.get("metadata")}")
                logger.debug("=" * 80)
                resources.extend(alb_resources)
                logger.debug("ALB DONE")
            except Exception as e:
                logger.warning(f"ALBDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("EBS START")
                resources.extend(EBSDiscovery.discover(reg))
                logger.debug("EBS DONE")
            except Exception as e:
                logger.warning(f"EBSDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("ECS START")
                resources.extend(ECSDiscovery.discover(reg))
                logger.debug("ECS DONE")
            except Exception as e:
                logger.warning(f"ECSDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("EKS START")
                resources.extend(EKSDiscovery.discover(reg))
                logger.debug("EKS DONE")
            except Exception as e:
                logger.warning(f"EKSDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("IGW START")
                resources.extend(IGWDiscovery.discover(reg))
                logger.debug("IGW DONE")
            except Exception as e:
                logger.warning(f"IGWDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("SUBNET START")
                resources.extend(SubnetDiscovery.discover(reg))
                logger.debug("SUBNET DONE")
            except Exception as e:
                logger.warning(f"SubnetDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("SECURITYGROUP START")
                resources.extend(SecurityGroupDiscovery.discover(reg))
                logger.debug("SECURITYGROUP DONE")
            except Exception as e:
                logger.warning(f"SecurityGroupDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("ROUTETABLE START")
                resources.extend(RouteTableDiscovery.discover(reg))
                logger.debug("ROUTETABLE DONE")
            except Exception as e:
                logger.warning(f"RouteTableDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("NATGATEWAY START")
                resources.extend(NatGatewayDiscovery.discover(reg))
                logger.debug("NATGATEWAY DONE")
            except Exception as e:
                logger.warning(f"NatGatewayDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("NETWORKINTERFACE START")
                resources.extend(NetworkInterfaceDiscovery.discover(reg))
                logger.debug("NETWORKINTERFACE DONE")
            except Exception as e:
                logger.warning(f"NetworkInterfaceDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("ELASTICIP START")
                resources.extend(ElasticIPDiscovery.discover(reg))
                logger.debug("ELASTICIP DONE")
            except Exception as e:
                logger.warning(f"ElasticIPDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("AUTOSCALING START")
                resources.extend(AutoScalingDiscovery.discover(reg))
                logger.debug("AUTOSCALING DONE")
            except Exception as e:
                logger.warning(f"AutoScalingDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("TARGETGROUP START")
                resources.extend(TargetGroupDiscovery.discover(reg))
                logger.debug("TARGETGROUP DONE")
            except Exception as e:
                logger.warning(f"TargetGroupDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("APIGATEWAY START")
                resources.extend(APIGatewayDiscovery.discover(reg))
                logger.debug("APIGATEWAY DONE")
            except Exception as e:
                logger.warning(f"APIGatewayDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("WAF START")
                resources.extend(WAFDiscovery.discover(reg))
                logger.debug("WAF DONE")
            except Exception as e:
                logger.warning(f"WAFDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("SECRETSMANAGER START")
                resources.extend(SecretsManagerDiscovery.discover(reg))
                logger.debug("SECRETSMANAGER DONE")
            except Exception as e:
                logger.warning(f"SecretsManagerDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("SSM START")
                resources.extend(SSMDiscovery.discover(reg))
                logger.debug("SSM DONE")
            except Exception as e:
                logger.warning(f"SSMDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("SNS START")
                resources.extend(SNSDiscovery.discover(reg))
                logger.debug("SNS DONE")
            except Exception as e:
                logger.warning(f"SNSDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("SQS START")
                resources.extend(SQSDiscovery.discover(reg))
                logger.debug("SQS DONE")
            except Exception as e:
                logger.warning(f"SQSDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("EVENTBRIDGE START")
                resources.extend(EventBridgeDiscovery.discover(reg))
                logger.debug("EVENTBRIDGE DONE")
            except Exception as e:
                logger.warning(f"EventBridgeDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("DYNAMODB START")
                resources.extend(DynamoDBDiscovery.discover(reg))
                logger.debug("DYNAMODB DONE")
            except Exception as e:
                logger.warning(f"DynamoDBDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("ELASTICACHE START")
                resources.extend(ElastiCacheDiscovery.discover(reg))
                logger.debug("ELASTICACHE DONE")
            except Exception as e:
                logger.warning(f"ElastiCacheDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("OPENSEARCH START")
                resources.extend(OpenSearchDiscovery.discover(reg))
                logger.debug("OPENSEARCH DONE")
            except Exception as e:
                logger.warning(f"OpenSearchDiscovery failed in region {reg}: {e}")

            try:
                logger.debug("EFS START")
                resources.extend(EFSDiscovery.discover(reg))
                logger.debug("EFS DONE")
            except Exception as e:
                logger.warning(f"EFSDiscovery failed in region {reg}: {e}")

        # Global providers

        try:
            logger.debug("S3 START")
            resources.extend(S3Discovery.discover())
            logger.debug("S3 DONE")
        except Exception as e:
            logger.warning(f"S3Discovery failed: {e}")

        try:
            logger.debug("IAM START")
            resources.extend(IAMDiscovery.discover())
            logger.debug("IAM DONE")
        except Exception as e:
            logger.warning(f"IAMDiscovery failed: {e}")

        try:
            logger.debug("CLOUDFRONT START")
            resources.extend(CloudFrontDiscovery.discover())
            logger.debug("CLOUDFRONT DONE")
        except Exception as e:
            logger.warning(f"CloudFrontDiscovery failed: {e}")

        try:
            logger.debug("ROUTE53 START")
            resources.extend(Route53Discovery.discover())
            logger.debug("ROUTE53 DONE")
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