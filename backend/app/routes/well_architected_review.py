from fastapi import APIRouter

from app.services.ai.well_architected_review import (
    WellArchitectedReviewService
)

router = APIRouter(

    prefix="/api/ai/architecture",

    tags=["Well Architected"]

)

service = WellArchitectedReviewService()


@router.post("/well-architected")
def review():

    return service.review_architecture()
