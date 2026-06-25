from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter(prefix="/api/ai/failure", tags=["AI Failure Analysis"])

class FailureAnalyzeRequest(BaseModel):
    resource: str

@router.post("/analyze")
async def analyze_failure(request: FailureAnalyzeRequest) -> Dict[str, Any]:
    try:
        from app.services.ai.architecture_service import ArchitectureService
        arch_service = ArchitectureService()
        
        # Craft a query that explicitly triggers the failure analysis engine
        # and specifies the resource name
        query = f"what happens if {request.resource} fails" 
        
        arch_data = arch_service.analyze(query)
        failure_data = arch_data.get("failure_context", {})
        
        # Ensure we return 404/not found behavior if the engine doesn't find the resource
        if not failure_data:
            raise HTTPException(status_code=404, detail=f"Could not analyze failure for resource: {request.resource}")
            
        return {
            "resource": failure_data.get("resource"),
            "severity": failure_data.get("severity"),
            "criticality_score": failure_data.get("criticality_score"),
            "blast_radius": failure_data.get("blast_radius"),
            "estimated_recovery": failure_data.get("estimated_recovery"),
            "business_impact": failure_data.get("business_impact", []),
            "affected_services": failure_data.get("affected_services", []),
            "likely_root_causes": failure_data.get("likely_root_causes", []),
            "recommendations": failure_data.get("recommendations", [])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
