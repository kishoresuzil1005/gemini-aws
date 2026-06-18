from fastapi import HTTPException

# Regional AWS Services
REGIONAL_SERVICES = {
    "ec2",
    "rds",
    "lambda",
    "ebs",
    "vpc",
    "alb",
    "ecs",
    "eks",
    "autoscaling",
    "cloudwatch",
    "elasticache",
}

# Global AWS Services
GLOBAL_SERVICES = {
    "s3",
    "iam",
    "route53",
    "cloudfront",
}

def validate_region(
    service_name: str,
    region: str | None,
) -> str:
    """
    Validate AWS service region.

    Examples:
    validate_region("ec2", "us-east-1") -> us-east-1
    validate_region("ec2", "global") -> HTTPException 400
    validate_region("s3", "global") -> global
    """
    if not region:
        raise HTTPException(
            status_code=400,
            detail="Region parameter is required"
        )

    service_name = service_name.lower()

    # Regional services cannot use global
    if (
        service_name in REGIONAL_SERVICES
        and region.lower() == "global"
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"{service_name.upper()} "
                "does not support global region"
            )
        )

    return region

def is_global_service(
    service_name: str
) -> bool:
    """
    Check if AWS service is global.
    """
    return service_name.lower() in GLOBAL_SERVICES

def is_regional_service(
    service_name: str
) -> bool:
    """
    Check if AWS service is regional.
    """
    return service_name.lower() in REGIONAL_SERVICES
