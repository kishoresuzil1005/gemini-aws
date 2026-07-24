"""
Defines the Execution Context used by the Analyzer Execution Engine.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ExecutionContext(BaseModel):
    """
    Immutable context that travels with the analyzer through the execution pipeline.
    Contains metadata necessary for observability, tracing, and deterministic reasoning.
    """
    request_id: str = Field(..., description="Unique identifier for the API request.")
    trace_id: str = Field(default="", description="Distributed trace ID.")
    span_id: str = Field(default="", description="Current execution span ID.")
    correlation_id: str = Field(default="", description="Correlation ID for business tracing.")
    session_id: str = Field(..., description="User session identifier.")
    
    intent: str = Field(..., description="The classified intent of the request.")
    resource_id: Optional[str] = Field(default=None, description="Primary resource being analyzed.")
    resource_type: Optional[str] = Field(default=None, description="Type of the primary resource.")
    
    provider: str = Field(default="system", description="Provider namespace (e.g., AWS, Azure).")
    cloud: str = Field(default="unknown", description="Target cloud environment.")
    region: str = Field(default="global", description="Target cloud region.")
    account_id: Optional[str] = Field(default=None, description="Target cloud account ID.")
    
    user_id: Optional[str] = Field(default=None, description="ID of the user making the request.")
    tenant_id: Optional[str] = Field(default=None, description="ID of the tenant/organization.")
    
    request_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the request originated.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional opaque context.")
