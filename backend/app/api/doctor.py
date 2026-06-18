from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db, ResourceDB
from app.services.optimization.recommendations import RecommendationEngine

router = APIRouter()


class AnalyzeRequest(BaseModel):
    resource_id: str


class AnalyzeResponse(BaseModel):
    resource_id: str
    resource_type: str
    health: str
    issues: list[str]
    recommendations: list[str]
    estimated_monthly_savings: float
    summary: str


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_resource(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    resource = (
        db.query(ResourceDB)
        .filter(
            ResourceDB.resource_id ==
            payload.resource_id
        )
        .first()
    )

    recommendations = RecommendationEngine.generate(db)

    matching = None

    for rec in recommendations:
        if rec.get("resource_id") == payload.resource_id:
            matching = rec
            break

    issues = []
    recs = []
    savings = 0.0
    health = "HEALTHY"

    if matching:
        health = "CRITICAL"

        issues.append(
            matching.get(
                "issue",
                "Optimization opportunity"
            )
        )

        recs.append(
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

    return AnalyzeResponse(
        resource_id=payload.resource_id,
        resource_type=(
            resource.resource_type
            if resource
            else "UNKNOWN"
        ),
        health=health,
        issues=issues,
        recommendations=recs,
        estimated_monthly_savings=savings,
        summary=(
            f"Potential savings "
            f"${savings:.2f}/month"
        )
    )
