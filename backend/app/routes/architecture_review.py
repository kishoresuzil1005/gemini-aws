from fastapi import APIRouter

from app.services.ai.architecture_review import ArchitectureReviewService

router = APIRouter(
    prefix="/api/ai/architecture",
    tags=["Architecture Review"]
)

service = ArchitectureReviewService()


@router.post("/review")
def review():

    return service.review()
