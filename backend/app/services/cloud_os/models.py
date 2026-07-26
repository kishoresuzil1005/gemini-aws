from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import datetime

from app.services.ai_orchestrator.models import AIRequest, AIResponse
from app.services.autonomous_engine.models import ExecutionPlan

class CloudOSUserContext(BaseModel):
    user_id: str
    organization_id: str
    roles: List[str]
    permissions: List[str]

class CloudOSMultiCloudConfig(BaseModel):
    providers: List[str] # AWS, Azure, GCP
    regions: List[str]
    environment: str # Prod, Non-Prod

class CloudOSRequest(BaseModel):
    request_id: str
    query: str
    target_id: Optional[str]
    user_context: CloudOSUserContext
    cloud_config: CloudOSMultiCloudConfig
    intent: str # Chat, Dashboard, Execution
    timestamp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

class CloudOSAction(BaseModel):
    action_type: str
    description: str
    payload: Any

class CloudOSResponse(BaseModel):
    response_id: str
    request_id: str
    intelligence_response: Optional[AIResponse]
    execution_plan: Optional[ExecutionPlan]
    suggested_actions: List[CloudOSAction]
    dashboard_data: Optional[Dict[str, Any]]
    ui_layout: str # Default, Exec, FinOps, SRE

class CloudOSHealthStatus(BaseModel):
    status: str # HEALTHY, DEGRADED, DOWN
    components: Dict[str, str]
    last_check: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

class CloudOSImplementationReport(BaseModel):
    coverage_report: str
    architecture_report: str
    readiness_report: str
    technical_debt: str
    known_limitations: List[str]
    implementation_status: str
