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

        print(
            f"[JOB] Generated "
            f"{len(recommendations)} "
            f"recommendations."
        )

    finally:

        db.close()
