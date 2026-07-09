from fastapi import APIRouter

from app.services.aws.regions_dashboard_service import (
    RegionsDashboardService
)

router = APIRouter(
    tags=["Regions"]
)

@router.get(
    "/api/v1/regions/dashboard"
)
def regions_dashboard():
    return RegionsDashboardService.get_regions()
