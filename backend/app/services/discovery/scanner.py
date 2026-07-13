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
                print("EC2 START")
                resources.extend(EC2Discovery.discover(reg))
                print("EC2 DONE")
            except Exception as e:
                logger.warning(f"EC2Discovery failed in region {reg}: {e}")

            try:
                print("RDS START")
                resources.extend(RDSDiscovery.discover(reg))
                print("RDS DONE")
            except Exception as e:
                logger.warning(f"RDSDiscovery failed in region {reg}: {e}")

            try:
                print("LAMBDA START")
                resources.extend(LambdaDiscovery.discover(reg))
                print("LAMBDA DONE")
            except Exception as e:
                logger.warning(f"LambdaDiscovery failed in region {reg}: {e}")

            try:
                print("VPC START")
                resources.extend(VPCDiscovery.discover(reg))
                print("VPC DONE")
            except Exception as e:
                logger.warning(f"VPCDiscovery failed in region {reg}: {e}")

            try:
                print("ALB START")
                resources.extend(ALBDiscovery.discover(reg))
                print("ALB DONE")
            except Exception as e:
                logger.warning(f"ALBDiscovery failed in region {reg}: {e}")

            try:
                print("EBS START")
                resources.extend(EBSDiscovery.discover(reg))
                print("EBS DONE")
            except Exception as e:
                logger.warning(f"EBSDiscovery failed in region {reg}: {e}")

            try:
                print("ECS START")
                resources.extend(ECSDiscovery.discover(reg))
                print("ECS DONE")
            except Exception as e:
                logger.warning(f"ECSDiscovery failed in region {reg}: {e}")

            try:
                print("EKS START")
                resources.extend(EKSDiscovery.discover(reg))
                print("EKS DONE")
            except Exception as e:
                logger.warning(f"EKSDiscovery failed in region {reg}: {e}")

            try:
                print("IGW START")
                resources.extend(IGWDiscovery.discover(reg))
                print("IGW DONE")
            except Exception as e:
                logger.warning(f"IGWDiscovery failed in region {reg}: {e}")

            try:
                print("SUBNET START")
                resources.extend(SubnetDiscovery.discover(reg))
                print("SUBNET DONE")
            except Exception as e:
                logger.warning(f"SubnetDiscovery failed in region {reg}: {e}")

            try:
                print("SECURITYGROUP START")
                resources.extend(SecurityGroupDiscovery.discover(reg))
                print("SECURITYGROUP DONE")
            except Exception as e:
                logger.warning(f"SecurityGroupDiscovery failed in region {reg}: {e}")

            try:
                print("ROUTETABLE START")
                resources.extend(RouteTableDiscovery.discover(reg))
                print("ROUTETABLE DONE")
            except Exception as e:
                logger.warning(f"RouteTableDiscovery failed in region {reg}: {e}")

            try:
                print("NATGATEWAY START")
                resources.extend(NatGatewayDiscovery.discover(reg))
                print("NATGATEWAY DONE")
            except Exception as e:
                logger.warning(f"NatGatewayDiscovery failed in region {reg}: {e}")

            try:
                print("NETWORKINTERFACE START")
                resources.extend(NetworkInterfaceDiscovery.discover(reg))
                print("NETWORKINTERFACE DONE")
            except Exception as e:
                logger.warning(f"NetworkInterfaceDiscovery failed in region {reg}: {e}")

            try:
                print("ELASTICIP START")
                resources.extend(ElasticIPDiscovery.discover(reg))
                print("ELASTICIP DONE")
            except Exception as e:
                logger.warning(f"ElasticIPDiscovery failed in region {reg}: {e}")

            try:
                print("AUTOSCALING START")
                resources.extend(AutoScalingDiscovery.discover(reg))
                print("AUTOSCALING DONE")
            except Exception as e:
                logger.warning(f"AutoScalingDiscovery failed in region {reg}: {e}")

            try:
                print("TARGETGROUP START")
                resources.extend(TargetGroupDiscovery.discover(reg))
                print("TARGETGROUP DONE")
            except Exception as e:
                logger.warning(f"TargetGroupDiscovery failed in region {reg}: {e}")

            try:
                print("APIGATEWAY START")
                resources.extend(APIGatewayDiscovery.discover(reg))
                print("APIGATEWAY DONE")
            except Exception as e:
                logger.warning(f"APIGatewayDiscovery failed in region {reg}: {e}")

            try:
                print("WAF START")
                resources.extend(WAFDiscovery.discover(reg))
                print("WAF DONE")
            except Exception as e:
                logger.warning(f"WAFDiscovery failed in region {reg}: {e}")

            try:
                print("SECRETSMANAGER START")
                resources.extend(SecretsManagerDiscovery.discover(reg))
                print("SECRETSMANAGER DONE")
            except Exception as e:
                logger.warning(f"SecretsManagerDiscovery failed in region {reg}: {e}")

            try:
                print("SSM START")
                resources.extend(SSMDiscovery.discover(reg))
                print("SSM DONE")
            except Exception as e:
                logger.warning(f"SSMDiscovery failed in region {reg}: {e}")

            try:
                print("SNS START")
                resources.extend(SNSDiscovery.discover(reg))
                print("SNS DONE")
            except Exception as e:
                logger.warning(f"SNSDiscovery failed in region {reg}: {e}")

            try:
                print("SQS START")
                resources.extend(SQSDiscovery.discover(reg))
                print("SQS DONE")
            except Exception as e:
                logger.warning(f"SQSDiscovery failed in region {reg}: {e}")

            try:
                print("EVENTBRIDGE START")
                resources.extend(EventBridgeDiscovery.discover(reg))
                print("EVENTBRIDGE DONE")
            except Exception as e:
                logger.warning(f"EventBridgeDiscovery failed in region {reg}: {e}")

            try:
                print("DYNAMODB START")
                resources.extend(DynamoDBDiscovery.discover(reg))
                print("DYNAMODB DONE")
            except Exception as e:
                logger.warning(f"DynamoDBDiscovery failed in region {reg}: {e}")

            try:
                print("ELASTICACHE START")
                resources.extend(ElastiCacheDiscovery.discover(reg))
                print("ELASTICACHE DONE")
            except Exception as e:
                logger.warning(f"ElastiCacheDiscovery failed in region {reg}: {e}")

            try:
                print("OPENSEARCH START")
                resources.extend(OpenSearchDiscovery.discover(reg))
                print("OPENSEARCH DONE")
            except Exception as e:
                logger.warning(f"OpenSearchDiscovery failed in region {reg}: {e}")

            try:
                print("EFS START")
                resources.extend(EFSDiscovery.discover(reg))
                print("EFS DONE")
            except Exception as e:
                logger.warning(f"EFSDiscovery failed in region {reg}: {e}")

        # Global providers

        try:
            print("S3 START")
            resources.extend(S3Discovery.discover())
            print("S3 DONE")
        except Exception as e:
            logger.warning(f"S3Discovery failed: {e}")

        try:
            print("IAM START")
            resources.extend(IAMDiscovery.discover())
            print("IAM DONE")
        except Exception as e:
            logger.warning(f"IAMDiscovery failed: {e}")

        try:
            print("CLOUDFRONT START")
            resources.extend(CloudFrontDiscovery.discover())
            print("CLOUDFRONT DONE")
        except Exception as e:
            logger.warning(f"CloudFrontDiscovery failed: {e}")

        try:
            print("ROUTE53 START")
            resources.extend(Route53Discovery.discover())
            print("ROUTE53 DONE")
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
        return scan_resul