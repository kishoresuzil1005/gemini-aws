from fastapi import APIRouter

from app.services.ai.architecture_scorer import ArchitectureScorer

router = APIRouter(

    prefix="/api/v1/architecture/reviews",

    tags=["Architecture Score"]

)

service = ArchitectureScorer()


@router.post("/score")
def score():

    return service.score()
