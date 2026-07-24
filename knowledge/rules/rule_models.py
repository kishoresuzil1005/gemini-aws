# knowledge/rules/rule_models.py
"""The central CanonicalRule schema."""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class CanonicalRule(BaseModel):
    """The authoritative universal representation of a rule/policy in the Catalog."""
    
    rule_id: str
    canonical_name: str
    display_name: str
    
    category: str           # e.g., "Security", "Cost Optimization"
    subcategory: str        # e.g., "IAM", "Idle Resources"
    
    provider: str
    services: List[str] = Field(default_factory=list)
    supported_resources: List[str] = Field(default_factory=list)
    
    description: str
    purpose: str
    
    severity: str           # CRITICAL, HIGH, MEDIUM, LOW
    priority: int
    risk_level: str
    compliance_framework: List[str] = Field(default_factory=list)
    
    rule_type: str
    evaluation_strategy: str
    
    # Payload for downstream policy engines
    conditions: Dict[str, Any] = Field(default_factory=dict)
    
    required_resources: List[str] = Field(default_factory=list)
    required_relationships: List[str] = Field(default_factory=list)
    required_properties: List[str] = Field(default_factory=list)
    
    expected_state: str = ""
    failure_state: str = ""
    remediation_summary: str = ""
    
    documentation_references: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    tags: Dict[str, str] = Field(default_factory=dict)
    
    version: str = "1.0"
    status: str = "DRAFT"   # DRAFT, APPROVED, PUBLISHED, DEPRECATED, ARCHIVED
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    created_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
