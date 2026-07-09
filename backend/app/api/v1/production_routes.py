from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter(prefix="/api/v1/ai/analysis/production", tags=["AI Production Readiness"])

class ProductionReviewRequest(BaseModel):
    provider: str = "aws"

@router.post("/review")
async def review_production_readiness(request: ProductionReviewRequest) -> Dict[str, Any]:
    try:
        from app.services.ai.architecture_service import ArchitectureService
        arch_service = ArchitectureService()
        
        # Trigger the production review engine by passing the relevant intent keyword
        query = "evaluate production readiness best practices"
        arch_data = arch_service.analyze(query)
        
        prod_data = arch_data.get("production_context", {})
        
        if not prod_data:
            raise HTTPException(status_code=500, detail="Failed to generate Production Readiness Report.")
            
        return {
            "production_ready": prod_data.get("production_ready", False),
            "readiness_score": prod_data.get("readiness_score", 0),
            "grade": prod_data.get("grade", "N/A"),
            "environment_type": prod_data.get("environment_type", "Unknown"),
            "critical_findings": prod_data.get("critical_findings", []),
            "recommendations": prod_data.get("recommendations", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checklist")
async def production_checklist(request: ProductionReviewRequest) -> Dict[str, Any]:
    try:
        from app.services.ai.architecture_service import ArchitectureService
        arch_service = ArchitectureService()
        
        query = "generate production checklist"
        arch_data = arch_service.analyze(query)
        
        prod_data = arch_data.get("production_context", {})
        chk_data = prod_data.get("detailed_checklist", {})
        
        if not chk_data:
            raise HTTPException(status_code=500, detail="Failed to generate Production Checklist.")
            
        return {
            "production_ready": chk_data.get("production_ready", False),
            "overall_score": chk_data.get("overall_score", 0),
            "grade": chk_data.get("grade", "N/A"),
            "summary": chk_data.get("summary", {}),
            "critical_items": chk_data.get("critical_items", []),
            "implementation_order": chk_data.get("implementation_order", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
