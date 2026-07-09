from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Intent Categories
# ---------------------------------------------------------

class IntentType(str, Enum):
    INVENTORY = "inventory"
    TOPOLOGY = "topology"
    DIAGNOSIS = "diagnosis"
    ROOT_CAUSE = "root_cause"
    MONITORING = "monitoring"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COST = "cost"
    MIGRATION = "migration"
    RECOMMENDATION = "recommendation"
    SELF_HEALING = "self_healing"
    GENERAL = "general"


# ---------------------------------------------------------
# Supported Cloud Resource Types
# ---------------------------------------------------------

class ResourceType(str, Enum):
    EC2 = "EC2"
    EBS = "EBS"
    VPC = "VPC"
    SUBNET = "Subnet"
    SECURITY_GROUP = "SecurityGroup"
    ROUTE_TABLE = "RouteTable"
    INTERNET_GATEWAY = "InternetGateway"
    NAT_GATEWAY = "NatGateway"
    NETWORK_INTERFACE = "NetworkInterface"
    ELASTIC_IP = "ElasticIP"

    RDS = "RDS"

    S3 = "S3"

    LAMBDA = "Lambda"

    ECS = "ECS"

    EKS = "EKS"

    LOAD_BALANCER = "LoadBalancer"

    TARGET_GROUP = "TargetGroup"

    AUTO_SCALING_GROUP = "AutoScalingGroup"

    IAM_ROLE = "IAMRole"

    IAM_USER = "IAMUser"

    IAM_POLICY = "IAMPolicy"

    API_GATEWAY = "ApiGateway"

    CLOUDFRONT = "CloudFront"

    ROUTE53 = "Route53"

    SNS = "SNS"

    SQS = "SQS"

    EVENTBRIDGE = "EventBridge"

    SECRETS_MANAGER = "SecretsManager"

    UNKNOWN = "Unknown"


# ---------------------------------------------------------
# Extracted Resource
# ---------------------------------------------------------

class CloudResource(BaseModel):
    resource_type: ResourceType

    name: Optional[str] = None

    resource_id: Optional[str] = None

    arn: Optional[str] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------
# Intent Result
# ---------------------------------------------------------

class IntentResult(BaseModel):
    intent: IntentType

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0
    )

    resources: List[CloudResource] = Field(default_factory=list)

    action: Optional[str] = None

    original_query: str

    metadata: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------
# Cloud Context (Future)
# ---------------------------------------------------------

class CloudContext(BaseModel):
    intent: IntentResult

    graph: Dict[str, Any] = Field(default_factory=dict)

    inventory: Dict[str, Any] = Field(default_factory=dict)

    metrics: Dict[str, Any] = Field(default_factory=dict)

    documentation: List[str] = Field(default_factory=list)

    recommendations: List[str] = Field(default_factory=list)
