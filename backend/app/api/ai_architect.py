from fastapi import APIRouter
from app.services.ai.architect_service import ArchitectService

router = APIRouter()

@router.post(
    "/api/ai/architect/analyze/{resource_id}"
)
def analyze_resource(resource_id: str):

    service = ArchitectService()

    return service.analyze(resource_id)
