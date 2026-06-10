class RiskEngine:

    @staticmethod
    def evaluate(recommendations):

        risks = []

        for r in recommendations:

            if r["severity"] == "high":

                risks.append({

                    "resource":
                    r["resource_id"],

                    "risk":
                    r["issue"]
                })

        return risks
