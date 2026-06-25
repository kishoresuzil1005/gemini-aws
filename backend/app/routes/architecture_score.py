from fastapi import APIRouter

from app.services.ai.architecture_scorer import ArchitectureScorer

router = APIRouter(

    prefix="/api/ai/architecture",

    tags=["Architecture Score"]

)

service = ArchitectureScorer()


@router.post("/score")
def score():

    return service.score()
