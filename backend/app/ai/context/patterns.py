"""
CloudOps AI Intent Patterns

This module contains keyword mappings used by the Intent Classifier.

It is intentionally data-only.
No classification logic should exist here.
"""

# ==========================================================
# Intent Keywords
# ==========================================================

INTENT_PATTERNS = {

    "inventory": [
        "list",
        "show",
        "display",
        "inventory",
        "resources",
        "discover",
        "find",
        "scan"
    ],

    "topology": [
        "topology",
        "diagram",
        "architecture",
        "dependency",
        "relationship",
        "graph",
        "connections",
        "network map"
    ],

    "diagnosis": [
        "diagnose",
        "issue",
        "problem",
        "error",
        "broken",
        "failing",
        "failure",
        "cannot",
        "can't",
        "unable",
        "why"
    ],

    "root_cause": [
        "root cause",
        "rca",
        "reason",
        "caused",
        "cause",
        "investigate"
    ],

    "monitoring": [
        "monitor",
        "monitoring",
        "metrics",
        "cpu",
        "memory",
        "disk",
        "latency",
        "network",
        "health"
    ],

    "performance": [
        "slow",
        "performance",
        "high cpu",
        "high memory",
        "response time",
        "latency",
        "throughput"
    ],

    "security": [
        "security",
        "vulnerability",
        "attack",
        "firewall",
        "public",
        "internet",
        "security group",
        "exposed"
    ],

    "cost": [
        "cost",
        "billing",
        "bill",
        "pricing",
        "expense",
        "spend",
        "monthly cost",
        "forecast"
    ],

    "optimization": [
        "optimize",
        "optimization",
        "recommend",
        "improve",
        "save",
        "rightsizing"
    ],

    "migration": [
        "migrate",
        "migration",
        "move",
        "azure",
        "gcp",
        "terraform"
    ],

    "automation": [
        "automation",
        "auto fix",
        "heal",
        "restart",
        "scale",
        "execute"
    ],

    "documentation": [
        "documentation",
        "docs",
        "guide",
        "manual",
        "reference"
    ]
}


# ==========================================================
# AWS Resource Keywords
# ==========================================================

RESOURCE_PATTERNS = {

    "EC2": [
        "ec2",
        "instance",
        "virtual machine"
    ],

    "RDS": [
        "rds",
        "database",
        "mysql",
        "postgres",
        "postgresql",
        "aurora"
    ],

    "S3": [
        "s3",
        "bucket",
        "object storage"
    ],

    "Lambda": [
        "lambda",
        "function",
        "serverless"
    ],

    "VPC": [
        "vpc",
        "virtual private cloud"
    ],

    "Subnet": [
        "subnet",
        "private subnet",
        "public subnet"
    ],

    "SecurityGroup": [
        "security group",
        "sg"
    ],

    "RouteTable": [
        "route table",
        "routing table"
    ],

    "InternetGateway": [
        "internet gateway",
        "igw"
    ],

    "NatGateway": [
        "nat gateway",
        "nat"
    ],

    "ElasticIP": [
        "elastic ip",
        "eip"
    ],

    "NetworkInterface": [
        "eni",
        "network interface"
    ],

    "LoadBalancer": [
        "alb",
        "elb",
        "load balancer"
    ],

    "TargetGroup": [
        "target group"
    ],

    "AutoScalingGroup": [
        "autoscaling",
        "auto scaling",
        "asg"
    ],

    "IAMRole": [
        "iam role",
        "role"
    ],

    "IAMUser": [
        "iam user",
        "user"
    ],

    "IAMPolicy": [
        "policy",
        "iam policy"
    ],

    "ECS": [
        "ecs",
        "container"
    ],

    "EKS": [
        "eks",
        "kubernetes"
    ],

    "CloudFront": [
        "cloudfront",
        "cdn"
    ],

    "Route53": [
        "route53",
        "dns"
    ],

    "SNS": [
        "sns",
        "notification"
    ],

    "SQS": [
        "sqs",
        "queue"
    ],

    "EventBridge": [
        "eventbridge",
        "event bus"
    ],

    "SecretsManager": [
        "secret",
        "secrets manager"
    ]
}


# ==========================================================
# Action Keywords
# ==========================================================

ACTION_PATTERNS = {

    "show": [
        "show",
        "display",
        "list",
        "view"
    ],

    "diagnose": [
        "diagnose",
        "analyze",
        "investigate",
        "debug"
    ],

    "fix": [
        "fix",
        "repair",
        "resolve"
    ],

    "monitor": [
        "monitor",
        "watch",
        "track"
    ],

    "migrate": [
        "migrate",
        "move",
        "convert"
    ],

    "optimize": [
        "optimize",
        "improve",
        "reduce cost"
    ]
}
