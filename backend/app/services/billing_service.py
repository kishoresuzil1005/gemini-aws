from sqlalchemy.orm import Session

from app.providers.aws.cost_explorer import CostExplorerAdapter
from app.services.cost.aggregator import CostAggregator
from app.services.cost.forecast import CostForecastEngine


class BillingService:

    def __init__(self, db: Session):
        self.db = db

    def get_summary(self):

        totals = CostAggregator.calculate_account_monthly(
            self.db,
            1
        )

        actual_cost = totals.get("total", 0.0)

        forecast = (
            CostForecastEngine.forecast_monthly_spend(
                actual_cost,
                days_elapsed=10
            )
        )

        return {
            "actual_cost": round(actual_cost, 2),
            "forecast": round(forecast, 2)
        }

    def get_cost_by_service(self):

        totals = CostAggregator.calculate_account_monthly(
            self.db,
            1
        )

        result = {}

        mapping = {
            "ec2": "Amazon EC2",
            "rds": "Amazon RDS",
            "s3": "Amazon S3",
            "lambda": "AWS Lambda",
            "ebs": "Amazon EBS",
            "alb": "Elastic Load Balancer",
            "sqs": "Amazon SQS",
            "sns": "Amazon SNS"
        }

        for key, label in mapping.items():

            value = totals.get(key, 0)

            if value > 0:
                result[label] = round(value, 2)

        return result

    def get_forecast(self):

        totals = CostAggregator.calculate_account_monthly(
            self.db,
            1
        )

        actual_cost = totals.get("total", 0.0)

        return round(
            CostForecastEngine.forecast_monthly_spend(
                actual_cost,
                days_elapsed=10
            ),
            2
        )
