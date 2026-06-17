
import datetime
import boto3
import time
from typing import Dict, List, Any

from app.providers.aws.auth import get_aws_client

# Cost Explorer Protection Cache
LAST_COST_REFRESH = {}
COST_TTL = 3600  # 1 hour


class CostExplorerAdapter:

    def __init__(self, cloud_account_id: int):
        self.cloud_account_id = cloud_account_id

        try:
            self.client = get_aws_client(
                "ce",
                cloud_account_id
            )
        except Exception:
            self.client = None

    def get_current_month_cost(self) -> float:
        """
        Returns month-to-date AWS spend.
        """
        cache_key = f"{self.cloud_account_id}_current_month"
        now = time.time()
        if cache_key in LAST_COST_REFRESH:
            cached_val, timestamp = LAST_COST_REFRESH[cache_key]
            if now - timestamp < COST_TTL:
                print(f"[COST CACHE] Protection HIT: current_month for account: {self.cloud_account_id}")
                return cached_val

        if self.client:

            try:

                today = datetime.date.today()

                start = (
                    today.replace(day=1)
                    .strftime("%Y-%m-%d")
                )

                end = today.strftime("%Y-%m-%d")

                if start == end:
                    return 0.0

                response = (
                    self.client.get_cost_and_usage(
                        TimePeriod={
                            "Start": start,
                            "End": end
                        },
                        Granularity="MONTHLY",
                        Metrics=[
                            "UnblendedCost"
                        ]
                    )
                )

                amount = float(
                    response["ResultsByTime"][0]
                    ["Total"]
                    ["UnblendedCost"]
                    ["Amount"]
                )

                result_val = round(amount, 2)
                LAST_COST_REFRESH[cache_key] = (result_val, now)
                return result_val

            except Exception as e:

                raise Exception(
                    f"AWS Cost Explorer failed: {e}"
                )

        return 0.0

    def get_cost_by_service(self) -> Dict[str, float]:
        """
        Returns service level spend.
        """
        cache_key = f"{self.cloud_account_id}_cost_by_service"
        now = time.time()
        if cache_key in LAST_COST_REFRESH:
            cached_val, timestamp = LAST_COST_REFRESH[cache_key]
            if now - timestamp < COST_TTL:
                print(f"[COST CACHE] Protection HIT: cost_by_service for account: {self.cloud_account_id}")
                return cached_val

        if self.client:

            try:

                today = datetime.date.today()

                start = (
                    today.replace(day=1)
                    .strftime("%Y-%m-%d")
                )

                end = today.strftime("%Y-%m-%d")

                if start == end:

                    start = (
                        today -
                        datetime.timedelta(days=30)
                    ).strftime("%Y-%m-%d")

                response = (
                    self.client.get_cost_and_usage(
                        TimePeriod={
                            "Start": start,
                            "End": end
                        },
                        Granularity="MONTHLY",
                        Metrics=[
                            "UnblendedCost"
                        ],
                        GroupBy=[
                            {
                                "Type": "DIMENSION",
                                "Key": "SERVICE"
                            }
                        ]
                    )
                )

                services = {}

                for group in (
                    response["ResultsByTime"][0]
                    .get("Groups", [])
                ):

                    name = group["Keys"][0]

                    amount = float(
                        group["Metrics"]
                        ["UnblendedCost"]
                        ["Amount"]
                    )

                    if amount > 0:

                        services[name] = round(
                            amount,
                            2
                        )

                LAST_COST_REFRESH[cache_key] = (services, now)
                if services:
                    return services

            except Exception as e:

                raise Exception(
                    f"AWS Cost Explorer failed: {e}"
                )

        return {}

    def get_daily_cost_trend(
        self,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Returns real AWS daily spend.
        """
        cache_key = f"{self.cloud_account_id}_daily_trend_{days}"
        now = time.time()
        if cache_key in LAST_COST_REFRESH:
            cached_val, timestamp = LAST_COST_REFRESH[cache_key]
            if now - timestamp < COST_TTL:
                print(f"[COST CACHE] Protection HIT: daily_trend for account: {self.cloud_account_id}")
                return cached_val

        if not self.client:
            return []

        try:

            end_date = (
                datetime.date.today()
            )

            start_date = (
                end_date -
                datetime.timedelta(days=days)
            )

            response = (
                self.client.get_cost_and_usage(
                    TimePeriod={
                        "Start":
                        start_date.strftime(
                            "%Y-%m-%d"
                        ),
                        "End":
                        end_date.strftime(
                            "%Y-%m-%d"
                        )
                    },
                    Granularity="DAILY",
                    Metrics=[
                        "UnblendedCost"
                    ]
                )
            )

            trend = []

            for item in (
                response["ResultsByTime"]
            ):

                trend.append({

                    "date":
                    item["TimePeriod"]
                    ["Start"],

                    "amount":
                    round(
                        float(
                            item["Total"]
                            ["UnblendedCost"]
                            ["Amount"]
                        ),
                        2
                    )
                })

            LAST_COST_REFRESH[cache_key] = (trend, now)
            return trend

        except Exception as e:

            print(
                f"Daily trend error: {e}"
            )

            return []

    def get_forecast_cost(self) -> float:
        """
        Returns forecasted month-end spend.
        """
        cache_key = f"{self.cloud_account_id}_forecast_cost"
        now = time.time()
        if cache_key in LAST_COST_REFRESH:
            cached_val, timestamp = LAST_COST_REFRESH[cache_key]
            if now - timestamp < COST_TTL:
                print(f"[COST CACHE] Protection HIT: forecast_cost for account: {self.cloud_account_id}")
                return cached_val

        if not self.client:
            return 0.0

        try:

            import calendar

            today = (
                datetime.date.today()
            )

            last_day = (
                calendar.monthrange(
                    today.year,
                    today.month
                )[1]
            )

            if today.day >= last_day - 1:
                res_val = self.get_current_month_cost()
                LAST_COST_REFRESH[cache_key] = (res_val, now)
                return res_val

            forecast = (
                self.client.get_cost_forecast(
                    TimePeriod={
                        "Start":
                        (
                            today +
                            datetime.timedelta(
                                days=1
                            )
                        ).strftime(
                            "%Y-%m-%d"
                        ),

                        "End":
                        today.replace(
                            day=last_day
                        ).strftime(
                            "%Y-%m-%d"
                        )
                    },
                    Metric=
                    "UNBLENDED_COST",
                    Granularity=
                    "MONTHLY"
                )
            )

            remaining = float(
                forecast["Total"]
                ["Amount"]
            )

            current = (
                self.get_current_month_cost()
            )

            if abs(current) < 0.01:
                return 0.0

            final_val = round(
                current + remaining,
                2
            )
            LAST_COST_REFRESH[cache_key] = (final_val, now)
            return final_val

        except Exception as e:

            raise Exception(
                f"AWS Cost Explorer failed: {e}"
            )
