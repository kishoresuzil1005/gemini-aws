from app.core.logging import get_logger
logger = get_logger(__name__)
from app.database import (
    SessionLocal
)

from app.services.optimization.recommendations import (
    RecommendationEngine
)


def run_optimization_job():

    db = SessionLocal()

    try:

        recommendations = (
            RecommendationEngine
            .generate(db)
        )

        logger.debug(
            f"[JOB] Generated "
            f"{len(recommendations)} "
            f"recommendations."
        )

    finally:

        db.close()
