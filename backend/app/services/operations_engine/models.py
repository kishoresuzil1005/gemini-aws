from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class OperationsFinding(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    resource_ids: List[str]

class OperationalRisk(BaseModel):
    overall_risk: str
    deployment_risk: str
    rollback_risk: str
    incident_risk: str

class OperationalHealth(BaseModel):
    status: str
    health_score: float
    service_health: Dict[str, str]
    application_health: Dict[str, str]
    infrastructure_health: Dict[str, str]

class IncidentAnalysis(BaseModel):
    incident_id: str
    severity: str
    priority: str
    affected_services: List[str]
    business_impact: str

class OperationalRecommendation(BaseModel):
    id: str
    title: str
    description: str
    impact: str
    effort: str
    resource_ids: List[str]

class Runbook(BaseModel):
    id: str
    title: str
    procedures: List[str]
    recovery_steps: List[str]
    validation_steps: List[str]

class MaintenanceWindow(BaseModel):
    id: str
    window_type: str
    start_time: str
    end_time: str
    affected_resources: List[str]

class OperationalTask(BaseModel):
    id: str
    task_name: str
    automation_candidate: bool

class OperationalPriority(BaseModel):
    level: str
    reason: str

class OperationalScore(BaseModel):
    overall_score: float
    category_scores: Dict[str, float]

class IncidentAssessment(BaseModel):
    status: str
    active_incidents: List[IncidentAnalysis]
    findings: List[OperationsFinding]

class AlertAssessment(BaseModel):
    status: str
    critical_alerts: int
    suppressed_alerts: int
    correlated_alerts: int
    findings: List[OperationsFinding]

class RunbookAssessment(BaseModel):
    status: str
    recommended_runbooks: List[Runbook]
    findings: List[OperationsFinding]

class ChangeImpactAssessment(BaseModel):
    status: str
    deployment_risk: str
    infrastructure_changes: List[str]
    rollback_risk: str
    findings: List[OperationsFinding]

class MaintenanceAssessment(BaseModel):
    status: str
    upcoming_windows: List[MaintenanceWindow]
    findings: List[OperationsFinding]

class OperationalHealthProfile(BaseModel):
    health: OperationalHealth
    findings: List[OperationsFinding]

class AutomationRecommendations(BaseModel):
    candidates: List[OperationalTask]
    findings: List[OperationsFinding]

class OperationsProfile(BaseModel):
    id: str
    target_id: str

class OperationalDashboard(BaseModel):
    incident_dashboard: Dict[str, Any]
    health_dashboard: Dict[str, Any]
    maintenance_dashboard: Dict[str, Any]
    automation_dashboard: Dict[str, Any]

class OperationalAssessment(BaseModel):
    id: str
    target_id: str
    incident_assessment: IncidentAssessment
    alert_assessment: AlertAssessment
    runbook_assessment: RunbookAssessment
    change_impact: ChangeImpactAssessment
    maintenance: MaintenanceAssessment
    health_profile: OperationalHealthProfile
    automation: AutomationRecommendations
    risk: OperationalRisk
    score: OperationalScore
    recommendations: List[OperationalRecommendation]
    dashboard: OperationalDashboard
    
    executive_summary: str = ""
    operations_summary: str = ""
    incident_summary: str = ""
    health_summary: str = ""
    runbook_summary: str = ""
    maintenance_summary: str = ""
    automation_summary: str = ""
    business_impact: str = ""
    ai_explanation: str = ""

class OperationsReport(BaseModel):
    coverage_report: str
    readiness_report: str
    known_limitations: List[str]
    technical_debt: List[str]
    implementation_status: str
