
import datetime
import boto3
from typing import Dict, List, Any

from app.providers.aws.auth import get_aws_client


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

                return round(amount, 2)

            except Exception as e:

                print(
                    f"Cost Explorer error: {e}"
                )

        try:

            from app.database import SessionLocal
            from app.services.cost.aggregator import (
                CostAggregator
            )

            db = SessionLocal()

            totals = (
                CostAggregator
                .calculate_account_monthly(
                    db,
                    self.cloud_account_id
                )
            )

            db.close()

            return float(
                totals.get(
                    "total",
                    0.0
                )
            )

        except Exception as e:

            print(
                f"Cost Aggregator error: {e}"
            )

            return 0.0

    def get_cost_by_service(self) -> Dict[str, float]:
        """
        Returns service level spend.
        """

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

                if services:
                    return services

            except Exception as e:

                print(
                    f"Cost Explorer service error: {e}"
                )

        try:

            from app.database import SessionLocal
            from app.services.cost.aggregator import (
                CostAggregator
            )

            db = SessionLocal()

            totals = (
                CostAggregator
                .calculate_account_monthly(
                    db,
                    self.cloud_account_id
                )
            )

            db.close()

            mapping = {
                "ec2":
                "Amazon Elastic Compute Cloud - Compute",

                "rds":
                "Amazon Relational Database Service",

                "s3":
                "Amazon Simple Storage Service",

                "alb":
                "Elastic Load Balancing",

                "lambda":
                "AWS Lambda",

                "sqs":
                "Amazon Simple Queue Service",

                "sns":
                "Amazon Simple Notification Service"
            }

            result = {}

            for key, value in totals.items():

                if (
                    key in mapping
                    and value > 0
                ):
                    result[
                        mapping[key]
                    ] = value

            return result

        except Exception as e:

            print(
                f"Aggregator service error: {e}"
            )

            return {}

    def get_daily_cost_trend(
        self,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Returns real AWS daily spend.
        """

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
                return (
                    self.get_current_month_cost()
                )

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

            return round(
                current + remaining,
                2
            )

        except Exception as e:

            print(
                f"Forecast error: {e}"
            )

            return 0.0
