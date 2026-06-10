from app.database import (
    SessionLocal
)

from app.services.ai.insights import (
    AIInsightEngine
)


def run_ai_job():

    db = SessionLocal()

    try:

        insights = (
            AIInsightEngine
            .generate(db)
        )

        print(
            "[JOB] AI Insights:"
        )

        print(
            insights
        )

    finally:

        db.close()
