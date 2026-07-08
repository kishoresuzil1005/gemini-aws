from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ResourceDependency(BaseModel):
    type: str
    id: str

class NormalizedResource(BaseModel):
    """
    Standardized resource object that all discovery modules must produce.
    """
    resource_id: str
    resource_type: str
    region: str
    provider: str = "AWS"
    name: Optional[str] = None
    status: Optional[str] = None
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    security: Dict[str, Any] = Field(default_factory=dict)
    monitoring: Dict[str, Any] = Field(default_factory=dict)
    cost: Dict[str, Any] = Field(default_factory=dict)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    tags: Dict[str, str] = Field(default_factory=dict)
    
    dependencies: List[ResourceDependency] = Field(default_factory=list)

class AWSDiscoveryModule:
    """
    Interface for AWS discovery modules.
    """
    @staticmethod
    def discover(region: str) -> List[NormalizedResource]:
        raise NotImplementedError("Each module must implement discover()")
