from fastapi import APIRouter
from app.database import SessionLocal

from app.services.anomaly.spend_detector import SpendAnomalyDetector
from app.services.anomaly.idle_detector import IdleResourceDetector

from app.services.forecast.forecast_engine import ForecastEngine

from app.services.optimization.recommendations import RecommendationEngine
from app.services.optimization.savings import SavingsCalculator

from app.services.budget.budget_engine import BudgetEngine
from app.providers.aws.cost_explorer import CostExplorerAdapter

from app.database import (
    BudgetDB,
    RemediationRequestDB
)

from app.services.remediation.approval import ApprovalService
from app.services.remediation.executor import RemediationExecutor

router = APIRouter(
    prefix="/operations",
    tags=["Operations"]
)


@router.get("/anomalies/spend")
def spend_anomalies():

    db = SessionLocal()

    result = SpendAnomalyDetector.detect(db)

    db.close()

    return result


@router.get("/anomalies/idle")
def idle_resources():

    db = SessionLocal()

    result = IdleResourceDetector.detect(db)

    db.close()

    return result


@router.get("/forecast")
def monthly_forecast():

    adapter = CostExplorerAdapter(1)

    current = (
        adapter
        .get_current_month_cost()
    )

    return (
        ForecastEngine
        .forecast_month(current)
    )


@router.get("/recommendations")
def recommendations():

    db = SessionLocal()

    result = (
        RecommendationEngine
        .generate(db)
    )

    db.close()

    return result


@router.get("/savings")
def savings():

    db = SessionLocal()

    recs = (
        RecommendationEngine
        .generate(db)
    )

    result = (
        SavingsCalculator
        .summarize(recs)
    )

    db.close()

    return result


@router.get("/budget")
def budget_status():

    db = SessionLocal()

    budget = (
        db.query(BudgetDB)
        .first()
    )

    adapter = CostExplorerAdapter(1)

    current = (
        adapter
        .get_current_month_cost()
    )

    if not budget:

        db.close()

        return {
            "status": "NO_BUDGET"
        }

    result = (
        BudgetEngine
        .evaluate(
            current,
            budget.limit_amount
        )
    )

    db.close()

    return result


@router.get("/remediation/pending")
def pending_remediations():

    db = SessionLocal()

    requests = (
        db.query(
            RemediationRequestDB
        )
        .filter(
            RemediationRequestDB.status
            == "PENDING"
        )
        .all()
    )

    result = []

    for r in requests:

        result.append({

            "id":
            r.id,

            "resource_id":
            r.resource_id,

            "resource_type":
            r.resource_type,

            "action":
            r.action,

            "status":
            r.status
        })

    db.close()

    return result


from pydantic import BaseModel

class CreateRemediationSchema(BaseModel):
    resource_id: str
    resource_type: str
    action: str


@router.post("/remediation/create")
def create_remediation(payload: CreateRemediationSchema):
    db = SessionLocal()
    req = RemediationRequestDB(
        resource_id=payload.resource_id,
        resource_type=payload.resource_type,
        action=payload.action,
        status="PENDING"
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    db.close()
    return {
        "status": "CREATED",
        "request_id": req.id,
        "resource_id": req.resource_id,
        "action": req.action
    }


@router.get("/remediation/all")
def get_all_remediations():
    db = SessionLocal()
    requests = (
        db.query(RemediationRequestDB)
        .order_by(RemediationRequestDB.created_at.desc())
        .all()
    )
    result = []
    for r in requests:
        result.append({
            "id": r.id,
            "resource_id": r.resource_id,
            "resource_type": r.resource_type,
            "action": r.action,
            "status": r.status,
            "execution_result": r.execution_result,
            "executed_at": r.executed_at,
            "created_at": r.created_at
        })
    db.close()
    return result


@router.post(
    "/remediation/{request_id}/approve"
)
def approve_remediation(
    request_id: int
):

    db = SessionLocal()

    request = (
        ApprovalService
        .approve(
            db,
            request_id
        )
    )

    db.close()

    if not request:

        return {
            "status": "NOT_FOUND"
        }

    return {
        "status": "APPROVED",
        "request_id": request_id
    }


@router.post(
    "/remediation/{request_id}/execute"
)
def execute_remediation(
    request_id: int
):

    db = SessionLocal()

    try:

        result = (
            RemediationExecutor
            .execute(
                db,
                request_id
            )
        )

        db.close()

        if not result:

            return {
                "status":
                "NOT_FOUND"
            }

        return {

            "status":
            "EXECUTED",

            "request_id":
            request_id
        }

    except Exception as e:

        db.close()

        return {

            "status":
            "FAILED",

            "error":
            str(e)
        }


@router.get("/system/jobs")
def jobs():

    return {

        "metric_job":
        "every 5 min",

        "cost_job":
        "every 1 hour",

        "optimization_job":
        "every 15 min",

        "anomaly_job":
        "every 15 min",

        "ai_job":
        "every 1 hour"
    }

