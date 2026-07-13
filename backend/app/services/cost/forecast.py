import logging
import time

logger = logging.getLogger("ForecastEngine")

class CostForecastEngine:
    @staticmethod
    def forecast_monthly_spend(current_month_accumulated: float, days_elapsed: int = 10) -> float:
        """
        Extrapolates current partial month expenses to predict overall end-of-month (30 day) run rate.
        Formula: (Accumulated Spend / Days Elapsed) * 30 days.
        """
        if days_elapsed <= 0:
            days_elapsed = 1 # boundary check
        
        daily_average = current_month_accumulated / days_elapsed
        projected_spend = daily_average * 30
        return round(projected_spend, 2)