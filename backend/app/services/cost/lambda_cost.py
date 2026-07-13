import logging
from app.services.cost.pricing_service import FALLBACK_PRICES

logger = logging.getLogger("LambdaCostCalculator")

class LambdaCostCalculator:
    @staticmethod
    def calculate_lambda_monthly(memory_size_mb: int = 128, monthly_requests: int = 1000000, avg_duration_ms: float = 180.0) -> float:
        """
        Computes monthly AWS Lambda processing fees combining request counts and execution durations.
        """
        lambda_pricing = FALLBACK_PRICES.get("Lambda", {})
        
        # 1. Compute duration charge
        # Convert duration to seconds and memory to GB
        duration_seconds = avg_duration_ms / 1000.0
        memory_gb = memory_size_mb / 1024.0
        total_gb_seconds = monthly_requests * duration_seconds * memory_gb
        
        compute_cost = total_gb_seconds * lambda_pricing.get("compute_gb_sec", 0.0000166667)
        
        # 2. Count requests cost
        request_cost = monthly_requests * lambda_pricing.get("request_rate", 0.0000002)
        
        return compute_cost + request_cos