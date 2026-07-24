# knowledge/extractors/extractor_context.py
"""Context models for the Extractor Engine."""

from typing import Dict, Any, Optional
from pydantic import BaseModel

class ExtractorContext(BaseModel):
    """Payload providing context to the Extractor Engine about the document."""
    provider: str
    source: str
    version: str
    document_id: str
    metadata: Dict[str, Any] = {}
