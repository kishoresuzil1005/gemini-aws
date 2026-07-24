# knowledge/providers/aws/connectors/monitoring_connector_models.py
"""Pydantic models for monitoring and operational knowledge objects.
These models define the canonical schema for the collected metadata, ensuring
that downstream analyzers receive standardized, provider-agnostic data.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class KnowledgeNamespace(BaseModel):
    namespace: str = Field(..., description="The AWS service namespace (e.g., AWS/EC2)")
    service_name: Optional[str] = Field(None, description="The human-readable service name")
    description: Optional[str] = Field(None, description="Description of the namespace")


class KnowledgeDimension(BaseModel):
    name: str = Field(..., description="The dimension name")
    description: Optional[str] = Field(None, description="Description of the dimension")


class KnowledgeStatistic(BaseModel):
    name: str = Field(..., description="Statistic name (e.g., Average, Sum, p99)")
    description: Optional[str] = Field(None)


class KnowledgeMetric(BaseModel):
    metric_name: str = Field(..., description="The name of the metric")
    namespace: str = Field(..., description="The namespace this metric belongs to")
    description: Optional[str] = Field(None, description="Description of what the metric measures")
    units: Optional[str] = Field(None, description="Standard units for the metric (e.g., Percent, Count, Bytes)")
    dimensions: List[KnowledgeDimension] = Field(default_factory=list, description="Supported dimensions")
    supported_statistics: List[KnowledgeStatistic] = Field(default_factory=list, description="Common statistics used for this metric")
    references: List[str] = Field(default_factory=list, description="Documentation references")


class KnowledgeAlarm(BaseModel):
    alarm_type: str = Field(..., description="Type of the alarm (e.g., Metric, Composite)")
    description: Optional[str] = Field(None)
    comparison_operators: List[str] = Field(default_factory=list, description="Supported comparison operators")
    states: List[str] = Field(default_factory=list, description="Possible states (OK, ALARM, INSUFFICIENT_DATA)")
    references: List[str] = Field(default_factory=list)


class KnowledgeEvent(BaseModel):
    event_name: str = Field(..., description="Name of the event")
    category: Optional[str] = Field(None, description="Event category")
    source: str = Field(..., description="Event source (e.g., ec2.amazonaws.com)")
    description: Optional[str] = Field(None)
    read_write_type: Optional[str] = Field(None, description="Read-only or Write-only classification")
    references: List[str] = Field(default_factory=list)


class KnowledgeOperation(BaseModel):
    operation_name: str = Field(..., description="The API operation name")
    service: str = Field(..., description="The associated service")
    description: Optional[str] = Field(None)
    references: List[str] = Field(default_factory=list)


class KnowledgeRunbook(BaseModel):
    document_name: str = Field(..., description="Name of the Systems Manager runbook/document")
    document_type: str = Field(..., description="Type of document (e.g., Automation, Command)")
    description: Optional[str] = Field(None)
    parameters: List[dict] = Field(default_factory=list, description="Parameters accepted by the runbook")
    references: List[str] = Field(default_factory=list)


class KnowledgeServiceEvent(BaseModel):
    event_type_code: str = Field(..., description="AWS Health event type code")
    service: str = Field(..., description="The service impacted")
    category: str = Field(..., description="Category (e.g., issue, accountNotification, scheduledChange)")
    description: Optional[str] = Field(None)


class KnowledgeRecommendation(BaseModel):
    check_id: str = Field(..., description="Trusted Advisor check ID")
    check_name: str = Field(..., description="Name of the check")
    category: str = Field(..., description="Category (e.g., security, cost_optimizing, fault_tolerance)")
    description: Optional[str] = Field(None)
    recommendation_guidance: Optional[str] = Field(None, description="Guidance provided by the check")
    references: List[str] = Field(default_factory=list)


class KnowledgeAutomation(BaseModel):
    automation_name: str = Field(...)
    description: Optional[str] = Field(None)
    references: List[str] = Field(default_factory=list)


class KnowledgeMaintenanceWindow(BaseModel):
    window_type: str = Field(...)
    description: Optional[str] = Field(None)
    references: List[str] = Field(default_factory=list)
