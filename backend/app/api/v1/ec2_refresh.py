from fastapi import APIRouter

from app.services.cache.ec2_cache import EC2Cache

router = APIRouter()


@router.post("/api/v1/ec2/refresh")
def refresh_ec2(
    region: str = "ap-south-1"
):

    EC2Cache.clear_region(region)

    return {
        "success": True,
        "message": f"EC2 cache cleared for region: {region}"
    }
