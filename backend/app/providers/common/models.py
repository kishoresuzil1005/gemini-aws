from typing import Dict, Any, Optional
from pydantic import BaseModel

class ProviderResponse(BaseModel):
    """Normalized response format universally shared across all cloud providers."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
