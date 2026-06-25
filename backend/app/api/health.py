from fastapi import APIRouter
from datetime import datetime
import psutil

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent
    }


@router.get("/ready")
async def readiness():
    return {
        "status": "ready"
    }


@router.get("/live")
async def liveness():
    return {
        "status": "alive"
    }
