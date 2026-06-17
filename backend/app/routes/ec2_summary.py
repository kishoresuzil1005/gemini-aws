from fastapi import APIRouter

from app.services.aws.ec2_summary_service import (
    EC2SummaryService
)
from app.services.cache.ec2_cache import EC2Cache

router = APIRouter()


@router.get("/api/ec2/summary")
def ec2_summary(
    region: str = "ap-south-1"
):

    cached = EC2Cache.get_summary(region)

    if cached:

        print(f"[EC2 CACHE] Summary HIT for region: {region}")

        return cached

    print(f"[EC2 CACHE] Summary MISS for region: {region}")

    service = EC2SummaryService(region)

    data = service.get_summary()

    EC2Cache.set_summary(region, data)

    return data

