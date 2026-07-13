class SavingsCalculator:

    @staticmethod
    def summarize(recommendations):

        monthly = sum(
            float(r.get("monthly_savings", r.get("savings", 0.0)))
            for r in recommendations
        )

        return {

            "monthly_savings":
            round(monthly, 2),

            "annual_savings":
            round(monthly * 12, 2)
        }

    @staticmethod
    def calculate_totals(recommendations):
        """
        Backward compatible mapping to summarize
        """
        return SavingsCalculator.summarize(recommendations)