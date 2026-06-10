import logging
from sqlalchemy.orm import Session
from app.database import ResourceDB
from app.services.cost.pricing_service import PricingService, FALLBACK_PRICES

logger = logging.getLogger("EC2Optimizer")

class EC2Optimizer:
    @staticmethod
    def analyze(db: Session, r: ResourceDB, pricing_service: PricingService) -> list:
        """
        Analyzes an EC2 resource for idle state or oversized limits.
        """
        recommendations = []
        if r.resource_type.upper() != "EC2":
            return recommendations

        # Simulated dynamic metrics (mock values for CPU and memory representing actual SRE scenarios)
        # We vary metrics deterministically based on the resource name or id to give high-fidelity results
        res_suffix = r.resource_id[-3:] if r.resource_id else "abc"
        char_sum = sum(ord(c) for c in res_suffix)
        
        avg_cpu = 2.4 if (char_sum % 2 == 0) else 14.5
        avg_memory = 12.0 if (char_sum % 3 == 0) else 45.0
        
        # Hourly and monthly cost for the current instance (usually t3.medium fallback in cost calculations)
        # If the name resembles 'large', treat it as t3.large, otherwise t3.medium
        current_type = "t3.medium"
        if r.name and "large" in r.name.lower():
            current_type = "t3.large"
        elif r.name and "micro" in r.name.lower():
            current_type = "t3.micro"
            
        current_rate = pricing_service.get_hourly_price("EC2", current_type, r.region or "us-east-1")
        current_monthly = current_rate * 24 * 30

        # Rule 1: Idle EC2 detection (CPU < 5%)
        if avg_cpu < 5.0:
            recommendations.append({
                "resource_id": r.resource_id,
                "resource_name": r.name or r.resource_id,
                "resource_type": "EC2",
                "severity": "critical",
                "issue": f"Idle EC2 Instance (Avg CPU: {avg_cpu}%)",
                "action": "Stop/Terminate",
                "current_specification": current_type,
                "recommended_specification": "Stopped",
                "savings": round(current_monthly, 2),
                "remediation_type": "AUTOMATIC"
            })
            
        # Rule 2: Rightsizing (Oversized: low utilization but running large types)
        elif current_type == "t3.large" and avg_cpu < 15.0 and avg_memory < 20.0:
            recommended_type = "t3.small"
            recom_rate = pricing_service.get_hourly_price("EC2", recommended_type, r.region or "us-east-1")
            recom_monthly = recom_rate * 24 * 30
            savings = max(0.0, current_monthly - recom_monthly)
            
            if savings > 1.0:
                recommendations.append({
                    "resource_id": r.resource_id,
                    "resource_name": r.name or r.resource_id,
                    "resource_type": "EC2",
                    "severity": "high",
                    "issue": f"Oversized EC2 Instance (Avg CPU: {avg_cpu}%, RAM: {avg_memory}%)",
                    "action": "Resize",
                    "current_specification": current_type,
                    "recommended_specification": recommended_type,
                    "savings": round(savings, 2),
                    "remediation_type": "MANUAL"
                })

        return recommendations
