from typing import Dict, Any

class SLAPolicy:
    """
    Adjusts the urgency, notification routing, and automated repair velocity 
    based on the business criticality (Gold, Silver, Bronze) of the impacted workload.
    """
    def determine_urgency(self, business_context: Dict[str, Any]) -> str:
        tier = business_context.get("sla_tier", "BRONZE").upper()
        if tier == "MISSION_CRITICAL" or tier == "GOLD":
            print(f"[SLAPolicy] {tier} workload impacted. Elevating repair priority to CRITICAL. Bypassing standard maintenance windows.")
            return "CRITICAL"
        elif tier == "SILVER":
            return "HIGH"
        return "NORMAL"