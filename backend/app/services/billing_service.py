from sqlalchemy.orm import Session

from app.providers.aws.cost_explorer import CostExplorerAdapter
from app.database import CloudAccountDB


class BillingService:

    def __init__(self, db: Session):
        self.db = db

    def get_summary(self):

        adapter = CostExplorerAdapter(1)

        return {
            "actual_cost": adapter.get_current_month_cost(),
            "forecast": adapter.get_forecast_cost()
        }

    def get_cost_by_service(self):

        adapter = CostExplorerAdapter(1)

        return adapter.get_cost_by_service()

    def get_forecast(self):

        adapter = CostExplorerAdapter(1)

        return adapter.get_forecast_cost()
