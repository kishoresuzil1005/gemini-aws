from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ResourceDB
from app.services.ai.insights import AIInsightEngine
from app.services.optimization.recommendations import RecommendationEngine
from app.services.cost.aggregator import CostAggregator

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    scan_id: Optional[str] = None


# Matching Response Schemas for Client validation compatibility
class LocalAIInsightsResponseSchema(BaseModel):
    executive_summary: str
    risks: List[str]
    savings_opportunities: List[str]
    recommendations: List[str]
    finops_score: int


class LocalAIChatResponseSchema(BaseModel):
    answer: str


class AnalyzeRequest(BaseModel):
    resource_id: str
    scan_id: Optional[str] = None


class AnalyzeResponse(BaseModel):
    resource_id: str
    resource_type: str
    health: str
    issues: list[str]
    recommendations: list[str]
    estimated_monthly_savings: float
    summary: str


@router.post(
    "/api/v1/ai/analysis/analyze",
    response_model=AnalyzeResponse
)
def analyze_resource(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    resource_id = payload.resource_id

    resource = (
        db.query(ResourceDB)
        .filter(
            ResourceDB.resource_id == resource_id
        )
        .first()
    )

    recommendations = RecommendationEngine.generate(db)

    matching = None

    for rec in recommendations:
        if rec.get("resource_id") == resource_id:
            matching = rec
            break

    issues = []
    recommendations_list = []
    savings = 0.0
    health = "HEALTHY"

    if matching:

        health = "CRITICAL"

        issues.append(
            matching.get(
                "issue",
                "Optimization opportunity detected"
            )
        )

        recommendations_list.append(
            matching.get(
                "recommendation",
                "Review resource"
            )
        )

        savings = float(
            matching.get(
                "monthly_savings",
                0
            )
        )

    summary = (
        f"Resource {resource_id} "
        f"can save approximately "
        f"${savings:.2f}/month."
    )

    return AnalyzeResponse(
        resource_id=resource_id,
        resource_type=(
            resource.resource_type
            if resource
            else "UNKNOWN"
        ),
        health=health,
        issues=issues,
        recommendations=recommendations_list,
        estimated_monthly_savings=savings,
        summary=summary
    )


@router.get(
    "/ai/insights",
    response_model=LocalAIInsightsResponseSchema
)
@router.get(
    "/api/ai/insights",
    response_model=LocalAIInsightsResponseSchema
)
def insights(db: Session = Depends(get_db)):
    """
    Evaluates resource configurations, waste ratios, and cost streams
    to deliver high-value architectural, security, and financial optimization feedback.
    """
    result = AIInsightEngine.generate(db)
    return result


@router.get(
    "/api/v1/ai/providers/health"
)
def get_provider_health():
    from app.services.ai.context_engine.provider_health_manager import ProviderHealthManager
    health_manager = ProviderHealthManager()
    return health_manager.summary()

