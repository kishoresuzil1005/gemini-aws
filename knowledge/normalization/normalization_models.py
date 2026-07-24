# knowledge/normalization/normalization_models.py
"""Multi-cloud abstract Canonical Knowledge Models."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class CanonicalModel(BaseModel):
    """Base for all canonical models."""
    canonical_id: str
    name: str
    description: Optional[str] = None
    tags: Dict[str, str] = {}
    metadata: Dict[str, Any] = {}

class CloudComputeInstance(CanonicalModel):
    """Canonical model for compute instances (EC2, VM, Compute Engine)."""
    instance_type: str
    status: str
    networks: List[str] = []

class ObjectStorageBucket(CanonicalModel):
    """Canonical model for object storage (S3, Blob Storage, Cloud Storage)."""
    is_public: bool = False
    encryption_enabled: bool = False

class IdentityRole(CanonicalModel):
    """Canonical model for IAM roles/Service Accounts."""
    permissions: List[str] = []

class MonitoringMetric(CanonicalModel):
    """Canonical model for telemetry metrics."""
    namespace: str
    dimensions: List[str] = []

class SecurityControl(CanonicalModel):
    """Canonical model for compliance and security rules."""
    severity: str
    remediation_url: Optional[str] = None
