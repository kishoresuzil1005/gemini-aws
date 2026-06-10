import logging
from app.services.cost.pricing_service import PricingService

logger = logging.getLogger("EC2CostCalculator")

class EC2CostCalculator:
    @staticmethod
    def calculate_instance_monthly(pricing_service: PricingService, instance_type: str, region: str = "us-east-1") -> float:
        """
        Computes monthly on-demand cost based on instance type and region fallback.
        Monthly formula: Hourly Rate * 24 Hours * 30 Days (720 hours).
        """
        hourly_rate = pricing_service.get_hourly_price("EC2", instance_type, region)
        return hourly_rate * 24 * 30
