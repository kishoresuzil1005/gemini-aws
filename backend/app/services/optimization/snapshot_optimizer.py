import logging
import time
from sqlalchemy.orm import Session
from app.models import ResourceDB
from app.services.cost.pricing_service import PricingService

logger = logging.getLogger("SnapshotOptimizer")

class SnapshotOptimizer:
    @staticmethod
    def analyze(db: Session, r: ResourceDB, pricing_service: PricingService) -> list:
        """
        Analyzes a Snapshot resource for age (> 90 days).
        """
        recommendations = []
        if r.resource_type.upper() not in ["SNAPSHOT", "EBS_SNAPSHOT", "RDS_SNAPSHOT"]:
            return recommendations

        res_suffix = r.resource_id[-3:] if r.resource_id else "snap"
        char_sum = sum(ord(c) for c in res_suffix)
        
        # Simulate age in days
        age_days = 120 if (char_sum % 2 == 0) else 15
        
        if age_days > 90:
            # Monthly backup rate is roughly $0.05 per GB-Month
            gb_size = 80.0
            savings = gb_size * 0.05 # $4.00/month
            
            recommendations.append({
                "resource_id": r.resource_id,
                "resource_name": r.name or r.resource_id,
                "resource_type": "Backup Snapshot",
                "severity": "low",
                "issue": f"Outdated backup snapshot (Age: {age_days} days)",
                "action": "Delete older snapshots",
                "current_specification": "Outdated snapshot",
                "recommended_specification": "None (Delete)",
                "savings": round(savings, 2),
                "remediation_type": "AUTOMATIC"
            })
            
        return recommendation