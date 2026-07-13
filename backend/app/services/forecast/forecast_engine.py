import calendar
import datetime


class ForecastEngine:

    @staticmethod
    def forecast_month(
        current_cost: float
    ):

        today = datetime.date.today()

        days_in_month = (
            calendar.monthrange(
                today.year,
                today.month
            )[1]
        )

        projected = (
            current_cost /
            max(today.day, 1)
        ) * days_in_month

        return {

            "current_cost":
            round(current_cost, 2),

            "forecast_cost":
            round(projected, 2)
        