import time

from app.database import SessionLocal
from app.models import (
    CostReportDB,
    CloudAccountDB
)

from app.providers.aws.cost_explorer import (
    CostExplorerAdapter
)


def run_cost_job():

    db = SessionLocal()

    try:

        accounts = (
            db.query(
                CloudAccountDB
            ).all()
        )

        for account in accounts:

            if (
                account.provider
                != "AWS"
            ):
                continue

            adapter = (
                CostExplorerAdapter(
                    account.id
                )
            )

            amount = (
                adapter
                .get_current_month_cost()
            )

            report = CostReportDB(

                provider="AWS",

                amount=amount,

                currency="USD",

                period_start=
                int(
                    time.time()
                    * 1000
                ),

                period_end=
                int(
                    time.time()
                    * 1000
                )
            )

            db.add(report)

        db.commit()

    finally:

        db.close()
