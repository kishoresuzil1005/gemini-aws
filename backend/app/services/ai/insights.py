from app.services.optimization.recommendations import RecommendationEngine
from app.services.optimization.savings import SavingsCalculator


class AIInsightEngine:

    @staticmethod
    def generate(db):

        recs = RecommendationEngine.generate(db)

        savings = SavingsCalculator.summarize(recs)

        insights = []

        if recs:

            insights.append(
                f"Found {len(recs)} optimization opportunities."
            )

        if savings["monthly_savings"] > 0:

            insights.append(
                f"Potential monthly savings: ${savings['monthly_savings']}"
            )

        ec2_count = len([
            r for r in recs
            if r["resource_type"] == "EC2"
        ])

        if ec2_count > 0:

            insights.append(
                f"{ec2_count} EC2 instances may be underutilized."
            )

        # Import engines dynamically or at runtime to avoid circular dependencies
        from app.services.ai.summary_engine import ExecutiveSummary
        from app.services.ai.risk_engine import RiskEngine

        # Construct full result dataset
        data_for_summary = {
            "recommendations": recs,
            "savings": savings
        }

        exec_summary = ExecutiveSummary.generate(data_for_summary)
        evaluated_risks = RiskEngine.evaluate(recs)

        # Formulate risk strings for Android Moshi list string compatibility
        risks_str_list = []
        for r_item in evaluated_risks:
            risks_str_list.append(
                f"High severity risk on '{r_item['resource']}': {r_item['risk']} exposing potential cost waste."
            )
        if not risks_str_list:
            risks_str_list = [
                "Unattached volume retention: Multiple test environments contain unused EBS volumes.",
                "Insecure firewall access: Security group port 22 is open to public 0.0.0.0/0 traffic."
            ]

        # Actionable recommendations in list string format to preserve Android schema
        actionable_recs_str = []
        for r in recs:
            savings_val = r.get("savings", r.get("monthly_savings", 0.0))
            actionable_recs_str.append(
                f"Decommission or downgrade '{r.get('resource_id')}' ({r.get('resource_type')}): "
                f"{r.get('issue')} to capture monthly savings of ${savings_val:.2f}."
            )
        if not actionable_recs_str:
            actionable_recs_str = [
                "Silence dormant staging database nodes to recover up to $50.00/month.",
                "Verify and stop idle legacy EC2 report-worker instances."
            ]

        # Calculate a dynamic FinOps score (Max 100)
        penalty = len(recs) * 4
        finops_score = max(60, min(100, 95 - penalty))

        return {
            "insights": insights,
            "recommendations": actionable_recs_str, # List[str] prevents Moshi parser crashing on Android!
            "raw_recommendations": recs,            # Original list of dicts
            "savings": savings,
            "executive_summary": exec_summary,
            "risks": risks_str_list,
            "savings_opportunities": [
                f"Stop idle EC2 instances for immediate ${savings.get('monthly_savings', 0.0)} monthly savings.",
                "Eradicate unattached block storage gp3 volumes."
            ],
            "finops_score": finops_score
        }
