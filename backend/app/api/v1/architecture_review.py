from fastapi import APIRouter

from app.services.ai.architecture_review import ArchitectureReviewService

router = APIRouter(
    prefix="/api/v1/architecture/reviews",
    tags=["Architecture Review"]
)

service = ArchitectureReviewService()


@router.post("/review")
def review():

    return service.review()
