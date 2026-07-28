from fastapi import APIRouter

from app.database import SessionLocal

from app.services.analysis.recommendation_service import RecommendationService

from app.services.optimization.savings import SavingsCalculator

router = APIRouter()


@router.get(
    "/api/v1/finops/recommendations"
)
def recommendations():

    db = SessionLocal()

    recs = (
        RecommendationService()
        .generate_finops(db)
    )

    db.close()

    return recs


@router.get(
    "/api/v1/finops/savings"
)
def savings():

    db = SessionLocal()

    recs = (
        RecommendationService()
        .generate_finops(db)
    )

    db.close()

    recs_list = []
    for r in recs:
        res_id = r.get("resource_id", r.get("resource"))
        saving_val = r.get("monthly_savings", r.get("saving"))
        if res_id and saving_val is not None:
            recs_list.append({
                "resource": res_id,
                "saving": round(float(saving_val), 2)
            })

    monthly_savings = sum(r["saving"] for r in recs_list)

    return {
        "monthly_savings": round(monthly_savings, 2),
        "recommendations": recs_list
    }
