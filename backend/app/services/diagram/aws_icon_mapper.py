from pathlib import Path

from app.services.diagram.layer_builder import LayerBuilder


class AWSIconMapper:

    #
    # Root folder containing AWS icons
    #
    ICON_ROOT = Path("assets/aws-icons")

    #
    # Possible filenames for each AWS service
    #
    SERVICE_ALIASES = {

        # ---------------- Compute ----------------

        "EC2": [
            "amazon-ec2",
            "ec2"
        ],

        "Lambda": [
            "aws-lambda",
            "lambda"
        ],

        "ECS": [
            "amazon-ecs",
            "ecs"
        ],

        "EKS": [
            "amazon-eks",
            "eks"
        ],

        "AutoScaling": [
            "amazon-ec2-auto-scaling",
            "auto-scaling"
        ],

        "AppRunner": [
            "aws-app-runner"
        ],

        "Batch": [
            "aws-batch"
        ],

        # ---------------- Database ----------------

        "RDS": [
            "amazon-rds",
            "rds"
        ],

        "DynamoDB": [
            "amazon-dynamodb",
            "dynamodb"
        ],

        "Redshift": [
            "amazon-redshift",
            "redshift"
        ],

        "ElastiCache": [
            "amazon-elasticache",
            "elasticache"
        ],

        # ---------------- Storage ----------------

        "S3": [
            "amazon-s3",
            "s3"
        ],

        "EBS": [
            "amazon-ebs",
            "ebs"
        ],

        "EFS": [
            "amazon-efs",
            "efs"
        ],

        "FSx": [
            "amazon-fsx",
            "fsx"
        ],

        # ---------------- Networking ----------------

        "VPC": [
            "amazon-vpc",
            "vpc"
        ],

        "Subnet": [
            "subnet"
        ],

        "SecurityGroup": [
            "security-group",
            "securitygroup"
        ],

        "Route53": [
            "amazon-route-53",
            "route53"
        ],

        "CloudFront": [
            "amazon-cloudfront",
            "cloudfront"
        ],

        "InternetGateway": [
            "internet-gateway"
        ],

        "NATGateway": [
            "nat-gateway"
        ],

        "ALB": [
            "application-load-balancer",
            "alb"
        ],

        "NLB": [
            "network-load-balancer",
            "nlb"
        ],

        # ---------------- Security ----------------

        "IAM": [
            "amazon-iam",
            "iam"
        ],

        "KMS": [
            "amazon-kms",
            "kms"
        ],

        "SecretsManager": [
            "amazon-secrets-manager",
            "secrets-manager"
        ],

        "GuardDuty": [
            "amazon-guardduty",
            "guardduty"
        ],

        "SecurityHub": [
            "amazon-security-hub",
            "security-hub"
        ],

        "Inspector": [
            "amazon-inspector",
            "inspector"
        ],

        "WAF": [
            "amazon-waf",
            "waf"
        ],

        # ---------------- Monitoring ----------------

        "CloudWatch": [
            "amazon-cloudwatch",
            "cloudwatch"
        ],

        "CloudTrail": [
            "amazon-cloudtrail",
            "cloudtrail"
        ],

        "SNS": [
            "amazon-sns",
            "sns"
        ],

        "SQS": [
            "amazon-sqs",
            "sqs"
        ],

        "EventBridge": [
            "amazon-eventbridge",
            "eventbridge"
        ]
    }

    def __init__(self):

        self.layer_builder = LayerBuilder()

        self.icon_cache = self._scan_icons()

    #
    # Scan icon folder once
    #
    def _scan_icons(self):

        cache = {}

        if not self.ICON_ROOT.exists():
            return cache

        for file in self.ICON_ROOT.rglob("*"):

            if file.is_file():

                cache[file.stem.lower()] = str(file)

        return cache

    #
    # Find matching icon
    #
    def find_icon(self, resource_type):

        aliases = self.SERVICE_ALIASES.get(

            resource_type,

            [resource_type.lower()]

        )

        for alias in aliases:

            path = self.icon_cache.get(alias.lower())

            if path:
                return path

        return None

    #
    # Build architecture with icons
    #
    def build(self):

        architecture = self.layer_builder.build()

        for resources in architecture["layers"].values():

            for resource in resources:

                resource["icon"] = self.find_icon(

                    resource["type"]

                )

        return architecture
