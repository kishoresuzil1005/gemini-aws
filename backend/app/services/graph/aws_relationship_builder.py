import logging
from sqlalchemy.orm import Session
from app.models import ResourceDB
from typing import List, Dict, Any

# Compute
from app.services.graph.builders.compute.ec2 import EC2GraphBuilder
from app.services.graph.builders.compute.autoscaling import AutoScalingGraphBuilder
from app.services.graph.builders.compute.target_group import TargetGroupGraphBuilder
from app.services.graph.builders.compute.alb import ALBGraphBuilder
from app.services.graph.builders.compute.ecs import ECSGraphBuilder
from app.services.graph.builders.compute.eks import EKSGraphBuilder

# Network
from app.services.graph.builders.network.vpc import VPCGraphBuilder
from app.services.graph.builders.network.subnet import SubnetGraphBuilder
from app.services.graph.builders.network.route_table import RouteTableGraphBuilder
from app.services.graph.builders.network.internet_gateway import InternetGatewayGraphBuilder
from app.services.graph.builders.network.nat_gateway import NatGatewayGraphBuilder
from app.services.graph.builders.network.security_group import SecurityGroupGraphBuilder
from app.services.graph.builders.network.network_interface import NetworkInterfaceGraphBuilder
from app.services.graph.builders.network.elastic_ip import ElasticIPGraphBuilder

# Storage
from app.services.graph.builders.storage.s3 import S3GraphBuilder
from app.services.graph.builders.storage.ebs import EBSGraphBuilder
from app.services.graph.builders.storage.efs import EFSGraphBuilder

# Database
from app.services.graph.builders.database.rds import RDSGraphBuilder
from app.services.graph.builders.database.dynamodb import DynamoDBGraphBuilder
from app.services.graph.builders.database.elasticache import ElastiCacheGraphBuilder
from app.services.graph.builders.database.opensearch import OpenSearchGraphBuilder

# Serverless
from app.services.graph.builders.serverless.lambda_builder import LambdaGraphBuilder
from app.services.graph.builders.serverless.api_gateway import APIGatewayGraphBuilder
from app.services.graph.builders.serverless.sns import SNSGraphBuilder
from app.services.graph.builders.serverless.sqs import SQSGraphBuilder
from app.services.graph.builders.serverless.eventbridge import EventBridgeGraphBuilder

# Security
from app.services.graph.builders.security.iam import IAMGraphBuilder
from app.services.graph.builders.security.waf import WAFGraphBuilder
from app.services.graph.builders.security.secrets_manager import SecretsManagerGraphBuilder

# Edge
from app.services.graph.builders.edge.cloudfront import CloudFrontGraphBuilder
from app.services.graph.builders.edge.route53 import Route53GraphBuilder

# Monitoring
from app.services.graph.builders.monitoring.cloudwatch import CloudWatchGraphBuilder

logger = logging.getLogger(__name__)

class AWSRelationshipBuilder:
    """
    Phase 2 Relationship Builder (Graph Builder v2).
    Acts as an orchestrator that passes the database inventory
    to modular category builders. ZERO Boto3 calls.
    """
    def __init__(self, db: Session):
        self.db = db

    def build(self) -> List[Dict[str, Any]]:
        # Read Inventory once
        resources = self.db.query(ResourceDB).all()
        relationships = []
        
        builders = [
            # Compute
            EC2GraphBuilder, AutoScalingGraphBuilder, TargetGroupGraphBuilder, 
            ALBGraphBuilder, ECSGraphBuilder, EKSGraphBuilder,
            # Network
            VPCGraphBuilder, SubnetGraphBuilder, RouteTableGraphBuilder,
            InternetGatewayGraphBuilder, NatGatewayGraphBuilder, 
            SecurityGroupGraphBuilder, NetworkInterfaceGraphBuilder, ElasticIPGraphBuilder,
            # Storage
            S3GraphBuilder, EBSGraphBuilder, EFSGraphBuilder,
            # Database
            RDSGraphBuilder, DynamoDBGraphBuilder, ElastiCacheGraphBuilder, OpenSearchGraphBuilder,
            # Serverless
            LambdaGraphBuilder, APIGatewayGraphBuilder, SNSGraphBuilder, 
            SQSGraphBuilder, EventBridgeGraphBuilder,
            # Security
            IAMGraphBuilder, WAFGraphBuilder, SecretsManagerGraphBuilder,
            # Edge
            CloudFrontGraphBuilder, Route53GraphBuilder,
            # Monitoring
            CloudWatchGraphBuilder
        ]
        
        try:
            for builder_cls in builders:
                relationships.extend(builder_cls.build(resources))
        except Exception as e:
            logger.error(f"Error building graph from inventory: {e}")
            
        return relationships