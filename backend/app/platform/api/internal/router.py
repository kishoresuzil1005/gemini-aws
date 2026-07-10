from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/api/internal", tags=["internal"])

@router.get("/health")
async def health_check():
    """
    Internal API for platform load balancers and Kubernetes readiness probes.
    """
    return {"status": "HEALTHY", "components": ["auth", "runtime", "database"]}
