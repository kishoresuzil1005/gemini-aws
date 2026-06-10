from fastapi import APIRouter
from app.database import (
    SessionLocal,
    MetricDB
)

router = APIRouter(
    tags=["Metrics"]
)


@router.get("/metrics/cpu/{resource_id}")
@router.get("/api/metrics/cpu/{resource_id}")
def cpu_metrics(
    resource_id: str
):

    db = SessionLocal()

    metrics = (
        db.query(MetricDB)
        .filter(
            MetricDB.resource_id
            == resource_id
        )
        .order_by(
            MetricDB.timestamp.desc()
        )
        .limit(50)
        .all()
    )

    result = []

    for metric in metrics:

        result.append({

            "timestamp":
            metric.timestamp,

            "value":
            metric.value
        })

    db.close()

    return result
