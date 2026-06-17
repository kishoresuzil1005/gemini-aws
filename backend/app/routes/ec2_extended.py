from fastapi import APIRouter

from app.services.aws.ec2_extended_service import (
    EC2ExtendedService
)
from app.services.cache.ec2_cache import EC2Cache

router = APIRouter()


@router.get("/api/ec2/extended")
def ec2_extended(
    region: str = "ap-south-1"
):

    cached = EC2Cache.get_extended(region)

    if cached:

        print(f"[EC2 CACHE] Extended HIT for region: {region}")

        return cached

    print(f"[EC2 CACHE] Extended MISS for region: {region}")

    service = EC2ExtendedService(region)

    data = service.get_extended_summary()

    EC2Cache.set_extended(region, data)

    return data

