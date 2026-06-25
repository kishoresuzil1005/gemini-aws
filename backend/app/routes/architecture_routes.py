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
        score_data = review_data.get("scoring", {})
        return {
            "overall_score": score_data.get("overall_score", 0),
            "grade": score_data.get("grade", "N/A"),
            "pillar_scores": score_data.get("pillar_scores", {}),
            "summary": review_data.get("inventory", {}),
            "findings": {
                "high": review_data.get("spofs", []),
                "medium": review_data.get("security_findings", []) + review_data.get("reliability_findings", []) + review_data.get("network_findings", []),
                "low": review_data.get("cost_findings", []) + review_data.get("monitoring_findings", [])
            },
            "recommendations": score_data.get("recommendations", []),
            "llm_review": result.get("answer", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/score")
async def score_architecture(request: ReviewRequest) -> Dict[str, Any]:
    try:
        from app.services.ai.architecture_service import ArchitectureService
        arch_service = ArchitectureService()
        # "review" keyword triggers the ArchitectureReview engine in the backend
        query = "review architecture" 
        arch_data = arch_service.analyze(query)
        review_data = arch_data.get("review_context", {})
        score_data = review_data.get("scoring", {})
        
        return {
            "overall_score": score_data.get("overall_score", 0),
            "grade": score_data.get("grade", "N/A"),
            "pillar_scores": score_data.get("pillar_scores", {}),
            "recommendations": score_data.get("recommendations", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/well-architected")
async def well_architected_review(request: ReviewRequest) -> Dict[str, Any]:
    try:
        from app.services.ai.architecture_service import ArchitectureService
        arch_service = ArchitectureService()
        query = "evaluate well architected review" 
        arch_data = arch_service.analyze(query)
        review_data = arch_data.get("review_context", {})
        score_data = review_data.get("scoring", {})
        wa_data = review_data.get("well_architected", {})
        
        # Format the output to match the expected API specification
        pillars_output = {}
        for pillar, data in wa_data.items():
            pillars_output[pillar] = {
                "score": data.get("score", 0),
                "strengths": data.get("strengths", []),
                "weaknesses": data.get("weaknesses", []),
                "recommendations": data.get("recommendations", [])
            }
            
        return {
            "overall_score": score_data.get("overall_score", 0),
            "grade": score_data.get("grade", "N/A"),
            "pillars": pillars_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
