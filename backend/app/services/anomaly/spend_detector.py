from app.models import CostReportDB


class SpendAnomalyDetector:

    THRESHOLD_PERCENT = 30

    @staticmethod
    def detect(db):

        reports = (
            db.query(CostReportDB)
            .order_by(
                CostReportDB.period_end.desc()
            )
            .limit(2)
            .all()
        )

        if len(reports) < 2:
            return []

        latest = reports[0]
        previous = reports[1]

        if previous.amount <= 0:
            return []

        increase = (
            (latest.amount - previous.amount)
            / previous.amount
        ) * 100

        if increase >= SpendAnomalyDetector.THRESHOLD_PERCENT:

            return [{
                "type": "SPEND_SPIKE",
                "severity": "HIGH",
                "message":
                    f"Spend increased by {round(increase,2)}%",
                "current":
                    latest.amount,
                "previous":
                    previous.amount
            }]

        return []
