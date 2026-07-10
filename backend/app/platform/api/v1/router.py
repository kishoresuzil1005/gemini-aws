from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/api/v1", tags=["v1"])

@router.post("/missions")
async def create_mission(payload: Dict[str, Any]):
    """
    V1 API for creating a new mission. Supported indefinitely.
    """
    return {"status": "success", "mission_id": "v1-mock-id", "message": "Mission started via V1 API."}
