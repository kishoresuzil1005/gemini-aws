from fastapi import APIRouter

from app.database import SessionLocal

from app.services.optimization.recommendations import RecommendationEngine

from app.services.optimization.savings import SavingsCalculator

router = APIRouter()


@router.get(
    "/optimization/recommendations"
)
@router.get(
    "/api/optimization/recommendations"
)
def recommendations():

    db = SessionLocal()

    recs = (
        RecommendationEngine
        .generate(db)
    )

    db.close()

    return recs


@router.get(
    "/optimization/savings"
)
@router.get(
    "/api/optimization/savings"
)
def savings():

    db = SessionLocal()

    recs = (
        RecommendationEngine
        .generate(db)
    )

    db.close()

    return (
        SavingsCalculator
        .summarize(recs)
    )
