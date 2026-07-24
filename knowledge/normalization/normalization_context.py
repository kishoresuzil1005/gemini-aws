# knowledge/normalization/normalization_context.py
"""Context models for the Normalization Engine."""

from typing import Dict, Any
from pydantic import BaseModel

class NormalizationContext(BaseModel):
    """Payload providing context to the Normalization Engine."""
    provider: str
    source: str
    document_id: str
    metadata: Dict[str, Any] = {}
