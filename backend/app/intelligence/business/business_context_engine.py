from app.core.logging import get_logger
logger = get_logger(__name__)
from typing import Dict, Any

class BusinessContextEngine:
    """
    Translates raw cloud resources (e.g. i-12345) into business context 
    (e.g. Payroll System, Mission Critical, Owner: John).
    """
    def get_context(self, resource_id: str) -> Dict[str, Any]:
        logger.debug(f"[BusinessContext] Mapping resource {resource_id} to business topology...")
        return {
            "application": "Payroll System",
            "department": "Finance",
            "criticality": "Mission Critical",
            "owner": "John",
            "estimated_revenue_risk_per_hour": 12000
        }
