import logging
from app.services.cost.pricing_service import PricingService

logger = logging.getLogger("RDSCostCalculator")

class RDSCostCalculator:
    @staticmethod
    def calculate_rds_monthly(pricing_service: PricingService, db_class: str, region: str = "us-east-1") -> float:
        """
        Computes monthly database engine fees based on instance sizes.
        """
        hourly_rate = pricing_service.get_hourly_price("RDS", db_class, region)
        return hourly_rate * 24 * 30
