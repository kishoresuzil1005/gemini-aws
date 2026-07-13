import logging
from app.services.cost.pricing_service import PricingService, FALLBACK_PRICES

logger = logging.getLogger("S3CostCalculator")

class S3CostCalculator:
    @staticmethod
    def calculate_s3_monthly(pricing_service: PricingService, size_gb: float = 250.0, storage_class: str = "Standard") -> float:
        """
        Computes monthly S3 bucket charges based on capacity in GB.
        Formula: Capacity (GB) * Rate per GB.
        """
        rates = FALLBACK_PRICES.get("S3", {})
        price_per_gb_month = rates.get(storage_class, rates.get("default", 0.023))
        return size_gb * price_per_gb_mont