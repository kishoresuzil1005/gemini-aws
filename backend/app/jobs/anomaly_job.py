from app.core.logging import get_logger
logger = get_logger(__name__)
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

        logger.debug(
            f"[JOB] Spend anomalies:"
            f" {len(spend)}"
        )

        logger.debug(
            f"[JOB] Idle resources:"
            f" {len(idle)}"
        )

    finally:

        db.close()
