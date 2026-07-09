from fastapi import APIRouter

from app.services.ai.production_checklist import (
    ProductionChecklistService
)

router = APIRouter(
    prefix="/api/v1/ai/production",
    tags=["Production Checklist"]
)

service = ProductionChecklistService()


@router.post("/checklist")
def checklist():

    return service.checklist()
