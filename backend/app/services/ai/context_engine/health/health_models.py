from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .provider_status import ProviderStatus

class ProviderHealth(BaseModel):
    """Data model storing the health of a single provider."""
    provider_name: str
    status: ProviderStatus = ProviderStatus.UNKNOWN
    last_checked: Optional[datetime] = None
    execution_time_ms: float = 0.0
    retry_count: int = 0
    cache_hit: bool = False
    error_message: Optional[str] = None
    warning_message: Optional[str] = None
    source: Optional[str] = None
    version: Optional[str] = None
