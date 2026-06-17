from fastapi import APIRouter

from app.services.aws.ec2_extended_service import (
    EC2ExtendedService
)

router = APIRouter()


@router.get("/api/ec2/extended")
def ec2_extended(
    region: str = "ap-south-1"
):

    service = EC2ExtendedService(
        region
    )

    return service.get_extended_summary()
