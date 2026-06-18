from sqlalchemy.orm import Session

from app.services.cost.cache import CostSummaryCache


class BillingService:

    def __init__(self, db: Session):
        self.db = db

    def get_summary(self):

        cached = CostSummaryCache.get()

        if not cached:
            return {
                "actual_cost": 0.0,
                "forecast": 0.0
            }

        return {
            "actual_cost": getattr(
                cached,
                "actualCost",
                0.0
            ),
            "forecast": getattr(
                cached,
                "forecastCost",
                0.0
            )
        }

    def get_cost_by_service(self):

        cached = CostSummaryCache.get()

        if not cached:
            return {}

        services = getattr(
            cached,
            "byService",
            []
        )

        if isinstance(services, dict):
            return services

        result = {}

        for item in services:

            if isinstance(item, dict):

                service_name = item.get(
                    "service",
                    "Unknown"
                )

                amount = float(
                    item.get(
                        "amount",
                        item.get("cost", 0.0)
                    )
                )

                result[service_name] = amount
            else:
                service_name = getattr(item, "service", "Unknown")
                amount = float(getattr(item, "amount", getattr(item, "cost", 0.0)))
                result[service_name] = amount

        return result

    def get_forecast(self):

        cached = CostSummaryCache.get()

        if not cached:
            return 0.0

        return round(
            getattr(
                cached,
                "forecastCost",
                0.0
            ),
            2
        )
