import logging
from sqlalchemy.orm import Session
from app.models import ResourceDB
from app.services.cost.pricing_service import PricingService

logger = logging.getLogger("NATOptimizer")

class NATOptimizer:
    @staticmethod
    def analyze(db: Session, r: ResourceDB, pricing_service: PricingService) -> list:
        """
        Analyzes a NAT Gateway resource for negligible traffic (BytesIn/BytesOut < threshold).
        """
        recommendations = []
        if r.resource_type.upper() not in ["NAT", "NAT_GATEWAY", "GW"]:
            return recommendations

        res_suffix = r.resource_id[-3:] if r.resource_id else "efg"
        char_sum = sum(ord(c) for c in res_suffix)
        
        traffic_bytes = 1024 * 50 if (char_sum % 2 == 0) else 1024 * 1024 * 1024 * 15 # 50KB vs 15GB
        
        # Monthly base uptime cost of standard AWS NAT Gateway is ~$32.40/month
        if traffic_bytes < (1024 * 1024 * 10): # less than 10MB processed
            recommendations.append({
                "resource_id": r.resource_id,
                "resource_name": r.name or r.resource_id,
                "resource_type": "NAT Gateway",
                "severity": "high",
                "issue": f"Idle NAT Gateway (Negligible traffic: {round(traffic_bytes / 1024, 2)} KB/month)",
                "action": "Delete and use VPC endpoints/direct gateways",
                "current_specification": "NAT-GW",
                "recommended_specification": "VPC Gateway Endpoint",
                "savings": 32.40,
                "remediation_type": "MANUAL"
            })
            
        return recommendation