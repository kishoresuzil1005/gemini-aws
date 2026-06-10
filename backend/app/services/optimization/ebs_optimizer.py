import logging
from sqlalchemy.orm import Session
from app.database import ResourceDB
from app.services.cost.pricing_service import PricingService

logger = logging.getLogger("EBSOptimizer")

class EBSOptimizer:
    @staticmethod
    def analyze(db: Session, r: ResourceDB, pricing_service: PricingService) -> list:
        """
        Analyzes an EBS Volume resource for unattached status (State == 'available' instead of 'in-use').
        """
        recommendations = []
        if r.resource_type.upper() not in ["EBS", "VOLUME"]:
            return recommendations

        # If a volume in our inventory is 'available' (unattached) or has a specific name hint, suggest deletion
        is_unused = r.status.lower() in ["available", "unattached", "unused"] or (r.name and "orphan" in r.name.lower())
        
        if is_unused:
            # Estimate volume size in GB based on resource_id or default to 100GB
            val_sz = 100.0
            if r.name and "gb" in r.name.lower():
                try:
                    # Extract numeric digits
                    val_sz = float("".join(c for c in r.name if c.isdigit())) or 100.0
                except ValueError:
                    pass
            
            # gp3 rate is $0.08 per GB/Month
            monthly_savings = val_sz * 0.08
            
            recommendations.append({
                "resource_id": r.resource_id,
                "resource_name": r.name or r.resource_id,
                "resource_type": "EBS Volume",
                "severity": "high",
                "issue": "Unused unattached EBS Disk Volume",
                "action": "Delete volume",
                "current_specification": f"{int(val_sz)} GB (gp3)",
                "recommended_specification": "None (Delete)",
                "savings": round(monthly_savings, 2),
                "remediation_type": "AUTOMATIC"
            })
            
        return recommendations
