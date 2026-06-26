from pathlib import Path
from functools import lru_cache


class IconAssetManager:
    """
    Resolves AWS SVG icon locations.

    This is the single source of truth for icon assets.
    """

    BASE_DIR = (
        Path(__file__)
        .resolve()
        .parents[3]
        / "assets"
        / "aws-icons"
    )

    ICON_MAP = {

        # -------------------------
        # Compute
        # -------------------------

        "EC2": "compute/ec2.svg",
        "Lambda": "compute/lambda.svg",
        "ECS": "compute/ecs.svg",
        "EKS": "compute/eks.svg",

        # -------------------------
        # Database
        # -------------------------

        "RDS": "database/rds.svg",
        "DynamoDB": "database/dynamodb.svg",

        # -------------------------
        # Networking
        # -------------------------

        "VPC": "networking/vpc.svg",
        "Subnet": "networking/subnet.svg",
        "SecurityGroup": "networking/security-group.svg",
        "ALB": "networking/alb.svg",

        # -------------------------
        # Storage
        # -------------------------

        "S3": "storage/s3.svg",
        "EBS": "storage/ebs.svg",
        "EFS": "storage/efs.svg",

        # -------------------------
        # Security
        # -------------------------

        "IAM": "security/iam.svg",
        "KMS": "security/kms.svg",
        "GuardDuty": "security/guardduty.svg",

        # -------------------------
        # Monitoring
        # -------------------------

        "CloudWatch": "monitoring/cloudwatch.svg",
        "CloudTrail": "monitoring/cloudtrail.svg",
        "SNS": "monitoring/sns.svg",
    }

    FALLBACK_ICON = None

    @classmethod
    @lru_cache(maxsize=256)
    def get_icon_path(cls, resource_type: str):
        """
        Returns the absolute icon path.

        Returns None if not found.
        """

        if not resource_type:
            return cls.FALLBACK_ICON

        resource_type = resource_type.strip()

        relative = cls.ICON_MAP.get(resource_type)

        if not relative:
            return cls.FALLBACK_ICON

        path = cls.BASE_DIR / relative

        if not path.exists():
            return cls.FALLBACK_ICON

        return str(path)

    @classmethod
    def icon_exists(cls, resource_type: str) -> bool:
        """
        Returns True if an icon exists.
        """
        return cls.get_icon_path(resource_type) is not None

    @classmethod
    def supported_icons(cls):
        """
        Returns every supported AWS resource.
        """
        return sorted(cls.ICON_MAP.keys())
