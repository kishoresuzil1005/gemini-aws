from fastapi import APIRouter, HTTPException
from app.services.graph.criticality_service import CriticalityService

router = APIRouter()
criticality_service = CriticalityService()

@router.get("/criticality/{resource_id}")
def get_criticality(resource_id: str):
    try:
        return criticality_service.calculate(resource_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-critical")
def get_top_critical():
    try:
        return criticality_service.top_critical()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
