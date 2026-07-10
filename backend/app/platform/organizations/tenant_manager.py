from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class Organization(BaseModel):
    org_id: str = str(uuid.uuid4())
    name: str
    tenant_domain: str
    subscription_tier: str = "FREE"
    created_at: datetime = datetime.utcnow()
    is_active: bool = True

class TenantManager:
    """
    Isolates data and logic for multiple companies (Multi-Tenancy).
    """
    def __init__(self):
        self.tenants: Dict[str, Organization] = {}

    def create_organization(self, name: str, domain: str) -> Organization:
        org = Organization(name=name, tenant_domain=domain)
        self.tenants[org.org_id] = org
        return org

    def get_organization(self, org_id: str) -> Optional[Organization]:
        return self.tenants.get(org_id)
