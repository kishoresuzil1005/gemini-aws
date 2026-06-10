class PromptBuilder:
    @staticmethod
    def build_analysis_prompt(context: dict) -> str:
        """
        Builds a comprehensive analysis prompt containing detailed platform metrics,
        billing states, and recommended cleanup actions.
        """
        resources = context.get("resources", [])
        costs = context.get("costs", {})
        recommendations = context.get("recommendations", [])
        
        # Summarize count of resources by type
        resource_counts = {}
        for r in resources:
            r_type = r.get("resource_type", "Unknown")
            resource_counts[r_type] = resource_counts.get(r_type, 0) + 1
            
        resource_summary_str = "\n".join([f"- {k}: {v}" for k, v in resource_counts.items()])
        if not resource_summary_str:
            resource_summary_str = "- No resources discovered currently in inventory."
            
        # Summarize recommendations
        rec_summary_list = []
        for rec in recommendations:
            rec_summary_list.append(
                f"- [{rec.get('severity', 'medium').upper()}] {rec.get('resource_type', 'Resource')}: "
                f"{rec.get('issue', 'Issue')} -> Action: {rec.get('action', 'Action')} (Potential Savings: ${rec.get('savings', 0.0)}/mo)"
            )
        rec_summary_str = "\n".join(rec_summary_list)
        if not rec_summary_str:
            rec_summary_str = "- No pending cost optimization recommendations."

        cost_breakdown_str = ""
        services_breakdown = costs.get("services", {})
        for svc, val in services_breakdown.items():
            cost_breakdown_str += f"- {svc}: ${val}/mo\n"

        prompt = f"""
Analyze this AWS environment and provide concrete cloud savings, performance advice and architectural risk analysis.

RESOURCE INVENTORY SUMMARY:
{resource_summary_str}

MONTH-TO-DATE COST SUMMARY:
- Current Actual Month-to-Date Spend: ${costs.get("actual_cost", 0.0)}
- Forecasted End-of-Month Spend: ${costs.get("forecast", 0.0)}
- Estimated running cost based on active inventory: ${costs.get("estimated_monthly", 0.0)}

COST BREAKDOWN BY SERVICE:
{cost_breakdown_str or "- No service breakdown available."}

ACTIVE COST OPTIMIZATION OPPORTUNITIES:
{rec_summary_str}

Generate the final output in structured JSON format with the following keys. Please return only raw JSON and do not include markdown wrap blocks.
{{
  "executive_summary": "Provide a high-level corporate summary summarizing current spend status, trend patterns, and opportunities for optimization.",
  "risks": [
    "Risk 1 description detailing security, availability, or rapid budget run-rates.",
    "Risk 2 description..."
  ],
  "savings_opportunities": [
    "Specifically mention specific savings actions and how much can be saved."
  ],
  "recommendations": [
    "General cloud architecture recommendations to follow."
  ],
  "finops_score": 85
}}
"""
        return prompt.strip()
