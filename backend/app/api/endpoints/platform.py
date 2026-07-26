from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.bootstrap import BootstrapManager
from knowledge.service.knowledge_client import KnowledgeClient

router = APIRouter()

# Dependency Injection Provider
def get_knowledge_client() -> KnowledgeClient:
    manager = BootstrapManager.get_instance()
    if not manager.is_ready or not manager.client:
        raise HTTPException(status_code=503, detail="Knowledge Platform is not ready")
    return manager.client

@router.get("/health", response_model=Dict[str, Any])
def health_check():
    manager = BootstrapManager.get_instance()
    health = manager.get_health()
    if health.get("status") in ["CRITICAL", "UNHEALTHY"]:
        raise HTTPException(status_code=503, detail=health)
    return health

@router.get("/readiness", response_model=Dict[str, Any])
def readiness_check():
    manager = BootstrapManager.get_instance()
    ready_state = manager.get_readiness()
    if not ready_state.get("ready"):
        raise HTTPException(status_code=503, detail=ready_state)
    return ready_state

@router.get("/metrics", response_model=Dict[str, Any])
def metrics_check():
    manager = BootstrapManager.get_instance()
    return manager.get_metrics()

@router.get("/self-test", response_model=Dict[str, Any])
def self_test_check():
    manager = BootstrapManager.get_instance()
    test_result = manager.run_self_test()
    if test_result.get("status") != "PASSED":
        raise HTTPException(status_code=500, detail=test_result)
    return test_result
