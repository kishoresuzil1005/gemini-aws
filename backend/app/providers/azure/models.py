from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.providers.common.models import ProviderResponse

class AzureResourceMetadata(BaseModel):
    """Generic base metadata for any Azure resource."""
    id: str
    name: str
    location: str
    type: str
