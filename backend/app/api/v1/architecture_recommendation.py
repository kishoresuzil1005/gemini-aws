from fastapi import APIRouter

from app.services.ai.architecture_recommendation import (
    ArchitectureRecommendationService
)

router = APIRouter(
    prefix="/api/v1/architecture/reviews",
    tags=["Architecture Recommendation"]
)

service = ArchitectureRecommendationService()


@router.post("/recommend")
def recommend():

    return service.recommend()
