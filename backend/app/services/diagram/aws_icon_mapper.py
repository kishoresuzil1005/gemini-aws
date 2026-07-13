from pathlib import Path


class AWSIconMapper:
    """
    Maps AWS resource types to official AWS Architecture icons.
    """

    BASE = "assets/aws-icons"

    ICONS = {

        #
        # Compute
        #

        "EC2": "compute/ec2.svg",
        "Lambda": "compute/lambda.svg",
        "ECS": "compute/ecs.svg",
        "EKS": "compute/eks.svg",

        #
        # Database
        #

        "RDS": "database/rds.svg",
        "DynamoDB": "database/dynamodb.svg",

        #
        # Networking
        #

        "VPC": "networking/vpc.svg",
        "Subnet": "networking/subnet.svg",
        "SecurityGroup": "networking/security-group.svg",
        "InternetGateway": "networking/internet-gateway.svg",
        "ALB": "networking/alb.svg",

        #
        # Storage
        #

        "S3": "storage/s3.svg",
        "EBS": "storage/ebs.svg",
        "EFS": "storage/efs.svg",

        #
        # Security
        #

        "IAM": "security/iam.svg",
        "KMS": "security/kms.svg",
        "GuardDuty": "security/guardduty.svg",

        #
        # Monitoring
        #

        "CloudWatch": "monitoring/cloudwatch.svg",
        "CloudTrail": "monitoring/cloudtrail.svg",
        "SNS": "monitoring/sns.svg"

    }

    DEFAULT_ICON = "general/resource.svg"

    def get_icon(self, resource_type: str):

        relative = self.ICONS.get(
            resource_type,
            self.DEFAULT_ICON
        )

        return str(
            Path(self.BASE) / relative
        