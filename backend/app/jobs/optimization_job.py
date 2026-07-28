from app.core.logging import get_logger
logger = get_logger(__name__)
from app.database import (
    SessionLocal
)

from app.services.analysis.recommendation_service import RecommendationService


def run_optimization_job():

    db = SessionLocal()

    try:

        recommendations = (
            RecommendationService()
            .generate_finops(db)
        )

        logger.debug(
            f"[JOB] Generated "
            f"{len(recommendations)} "
            f"recommendations."
        )

    finally:

        db.close()
