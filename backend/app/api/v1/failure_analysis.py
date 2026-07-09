from fastapi import APIRouter

from pydantic import BaseModel

from app.services.ai.failure_analysis import FailureAnalysisService


router = APIRouter(

    prefix="/api/v1/ai/analysis",

    tags=["Failure Analysis"]

)


service = FailureAnalysisService()


class FailureRequest(BaseModel):

    resource: str


@router.post("/analyze")
def analyze(request: FailureRequest):

    return service.analyze(request.resource)
