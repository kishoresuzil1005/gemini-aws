from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.providers.common.models import ProviderResponse

class KubernetesResourceMetadata(BaseModel):
    """Generic metadata for any Kubernetes resource."""
    id: str
    name: str
    namespace: Optional[str] = None
    type: str
    cluster_name: str = "default"
