from app.database import (
    SessionLocal
)

from app.services.anomaly.spend_detector import (
    SpendAnomalyDetector
)

from app.services.anomaly.idle_detector import (
    IdleResourceDetector
)


def run_anomaly_job():

    db = SessionLocal()

    try:

        spend = (
            SpendAnomalyDetector
            .detect(db)
        )

        idle = (
            IdleResourceDetector
            .detect(db)
        )

        print(
            f"[JOB] Spend anomalies:"
            f" {len(spend)}"
        )

        print(
            f"[JOB] Idle resources:"
            f" {len(idle)}"
        )

    finally:

        db.close()
