from enum import Enum

class Intent(str, Enum):

    EC2 = "ec2"

    RDS = "rds"

    S3 = "s3"

    VPC = "vpc"

    SUBNET = "subnet"

    SECURITY_GROUP = "security_group"

    SECURITY_AUDIT = "security_audit"

    PUBLIC_EXPOSURE = "public_exposure"

    COST = "cost"

    MONITORING = "monitoring"

    UNKNOWN = "unknown"
