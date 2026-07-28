from app.core.logging import get_logger
logger = get_logger(__name__)
from pydantic import BaseModel
from typing import Dict

class SubscriptionTier(BaseModel):
    name: str
    max_missions_per_month: int
    allowed_features: list

class LicenseManager:
    """
    Manages SaaS subscription limits and billing gates.
    """
    def __init__(self):
        self.tiers = {
            "FREE": SubscriptionTier(name="FREE", max_missions_per_month=10, allowed_features=["planning"]),
            "PRO": SubscriptionTier(name="PRO", max_missions_per_month=1000, allowed_features=["planning", "execution", "agents"]),
            "ENTERPRISE": SubscriptionTier(name="ENTERPRISE", max_missions_per_month=999999, allowed_features=["all"])
        }
        
    def check_limit(self, tenant_tier: str, feature: str) -> bool:
        tier = self.tiers.get(tenant_tier, self.tiers["FREE"])
        if "all" in tier.allowed_features or feature in tier.allowed_features:
            return True
        return False
        
class UsageMeter:
    """
    Tracks API and compute usage for billing purposes.
    """
    def record_usage(self, tenant_id: str, resource_type: str, quantity: float):
        logger.debug(f"[UsageMeter] Billed Tenant {tenant_id}: {quantity} of {resource_type}")
