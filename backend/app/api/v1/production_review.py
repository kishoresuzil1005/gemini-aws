from fastapi import APIRouter

from app.services.ai.production_review import ProductionReviewService


router = APIRouter(

    prefix="/api/v1/ai/production",

    tags=["Production Review"]

)

service = ProductionReviewService()


@router.post("/review")
def review():

    return service.review()
