from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from app.services.ai.rag_service import RAGService

router = APIRouter(prefix="/api/ai/architecture", tags=["AI Architecture"])
rag_service = RAGService()

class ReviewRequest(BaseModel):
    provider: str = "aws"
    query: str = "Review my AWS architecture"

@router.post("/review")
async def review_architecture(request: ReviewRequest) -> Dict[str, Any]:
    try:
        # Trigger RAG Service with a review intent query
        # Since 'review' is in the query, ArchitectureService will automatically
        # trigger the ArchitectureReview engine.
        result = rag_service.query_rag(query=request.query)
        
        # We can extract the raw context built by ArchitectureService if we want
        # to expose the structured findings in the API response payload.
        # Note: The 'answer' contains the LLM's full text review.
        
        architecture_context = {}
        # We need a small workaround to grab the raw review context since RAG Service 
        # usually returns it formatted. For the API, we can call ArchitectureService directly.
        from app.services.ai.architecture_service import ArchitectureService
        arch_service = ArchitectureService()
        arch_data = arch_service.analyze(request.query)
        review_data = arch_data.get("review_context", {})
        
        # Build the final response structure
        return {
            "architecture_score": 81, # Example static score, to be replaced by scoring engine later
            "summary": review_data.get("inventory", {}),
            "findings": {
                "high": review_data.get("spofs", []),
                "medium": review_data.get("security_findings", []) + review_data.get("reliability_findings", []) + review_data.get("network_findings", []),
                "low": review_data.get("cost_findings", []) + review_data.get("monitoring_findings", [])
            },
            "recommendations": [
                "Enable Auto Scaling.",
                "Configure Multi-AZ RDS.",
                "Enable CloudTrail.",
                "Configure AWS Backup."
            ],
            "llm_review": result.get("answer", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
