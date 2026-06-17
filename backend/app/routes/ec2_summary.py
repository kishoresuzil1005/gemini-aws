from fastapi import APIRouter

from app.services.aws.ec2_summary_service import (
    EC2SummaryService
)

router = APIRouter()


@router.get("/api/ec2/summary")
def ec2_summary(
    region: str = "ap-south-1"
):

    service = EC2SummaryService(
        region
    )

    return service.get_summary()
