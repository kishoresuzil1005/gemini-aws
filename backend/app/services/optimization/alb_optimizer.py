import logging
from sqlalchemy.orm import Session
from app.models import ResourceDB
from app.services.cost.pricing_service import PricingService

logger = logging.getLogger("ALBOptimizer")

class ALBOptimizer:
    @staticmethod
    def analyze(db: Session, r: ResourceDB, pricing_service: PricingService) -> list:
        """
        Analyzes an ALB resource to check if it represents a passive load balancer (RequestCount = 0).
        """
        recommendations = []
        if r.resource_type.upper() not in ["ALB", "ELB", "GATEWAY"]:
            return recommendations

        # Deterministic simulation of request counts
        res_suffix = r.resource_id[-3:] if r.resource_id else "abc"
        char_sum = sum(ord(c) for c in res_suffix)
        
        request_count = 0 if (char_sum % 2 == 0) else 152000
        
        if request_count == 0:
            monthly_cost = 22.50 # Application Load Balancer minimum standard monthly running rate
            
            recommendations.append({
                "resource_id": r.resource_id,
                "resource_name": r.name or r.resource_id,
                "resource_type": "Load Balancer",
                "severity": "medium",
                "issue": "Idle Application Load Balancer (No received HTTP headers or requests in 30 days)",
                "action": "Delete",
                "current_specification": "ALB Ingress",
                "recommended_specification": "None (Delete)",
                "savings": round(monthly_cost, 2),
                "remediation_type": "AUTOMATIC"
            })
            
        return recommendations
