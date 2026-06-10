import datetime
from sqlalchemy.orm import Session
from app.database import CloudAccountDB
from app.providers.aws.cost_explorer import CostExplorerAdapter

class BillingService:
    def __init__(self, db: Session = None, cloud_account_id: int = None):
        self.db = db
        self.cloud_account_id = cloud_account_id
        self._adapter = None

    def _get_adapter(self) -> CostExplorerAdapter:
        if self._adapter:
            return self._adapter

        account_id = self.cloud_account_id
        if not account_id and self.db:
            # Attempt to discover first active AWS account
            acct = self.db.query(CloudAccountDB).filter(CloudAccountDB.provider == "AWS").first()
            if acct:
                account_id = acct.id

        self._adapter = CostExplorerAdapter(account_id or 1)
        return self._adapter

    def get_summary(self) -> dict:
        adapter = self._get_adapter()
        actual_val = adapter.get_current_month_cost()
        forecast_val = adapter.get_forecast_cost()
        services = adapter.get_cost_by_service()

        return {
            "actual_cost": actual_val,
            "forecast": forecast_val,
            "services": services
        }

    def get_cost_by_service(self) -> dict:
        adapter = self._get_adapter()
        return adapter.get_cost_by_service()

    def get_forecast(self) -> float:
        adapter = self._get_adapter()
        return adapter.get_forecast_cost()
