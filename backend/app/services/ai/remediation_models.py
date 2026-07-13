from pydantic import BaseModel
from typing import List, Optional

class RemediationPlan(BaseModel):
    recommendation_id: str
    resource_id: str
    issue: str
    priority: str
    terraform: str
    aws_cli: str
    cloudformation: str
    manual_steps: str
    rollback: str
    estimated_time: str
    downtime: str
    risk: st