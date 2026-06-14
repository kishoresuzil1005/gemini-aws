from fastapi import APIRouter
from app.services.region_service import RegionService

router = APIRouter(
    prefix="/api/regions",
    tags=["Regions"]
)

@router.get("")
def get_regions():
    return {
        "success": True,
        "regions": RegionService.get_regions()
    }
