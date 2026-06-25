from app.services.cost.pricing_service import PricingService


class CostAnalyzer:

    @staticmethod
    def ec2_monthly_cost(
        pricing_service,
        instance_type,
        region
    ):

        try:
            if hasattr(pricing_service, "get_ec2_hourly_price"):
                price = pricing_service.get_ec2_hourly_price(instance_type, region)
            else:
                price = pricing_service.get_hourly_price("EC2", instance_type, region or "us-east-1")

            return round(
                price * 730,
                2
            )

        except Exception:

            return 0.0

    @staticmethod
    def rds_monthly_cost(
        pricing_service,
        instance_class,
        region
    ):

        try:
            if hasattr(pricing_service, "get_rds_hourly_price"):
                price = pricing_service.get_rds_hourly_price(instance_class, region)
            else:
                price = pricing_service.get_hourly_price("RDS", instance_class, region or "us-east-1")

            return round(
                price * 730,
                2
            )

        except Exception:

            return 0.0
