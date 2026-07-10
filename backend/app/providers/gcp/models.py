from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.providers.common.models import ProviderResponse

class GCPResourceMetadata(BaseModel):
    """Generic base metadata for any GCP resource."""
    id: str
    name: str
    zone_or_region: str
    type: str
    project_id: str
