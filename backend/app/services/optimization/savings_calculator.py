import logging

logger = logging.getLogger("SavingsCalculator")

class SavingsCalculator:
    @staticmethod
    def calculate_totals(recommendations: list) -> dict:
        """
        Compiles total potential monthly and annual savings metrics.
        """
        monthly_total = sum(float(r.get("savings", 0.0)) for r in recommendations)
        annual_total = monthly_total * 12
        
        return {
            "monthly_savings": round(monthly_total, 2),
            "annual_savings": round(annual_total, 2)
        }
