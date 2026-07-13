class BudgetEngine:

    @staticmethod
    def evaluate(
        current_cost,
        budget_limit
    ):

        if current_cost > budget_limit:

            return {

                "status":
                "EXCEEDED",

                "over_by":
                round(
                    current_cost -
                    budget_limit,
                    2
                )
            }

        return {

            "status":
            "OK",

            "remaining":
            round(
                budget_limit -
                current_cost,
                2
            )
        }