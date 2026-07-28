# knowledge/extractors/extractor_report.py
"""Reporting models for the Extractor Engine."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ExtractionReport(BaseModel):
    """Summarizes the outcome of an extraction run."""
    extraction_id: str
    provider: str
    source: str
    document_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    duration_ms: int = 0
    entities_extracted: int = 0
    relationships_found: int = 0
    candidate_counts: Dict[str, int] = Field(default_factory=dict)
    average_confidence: float = 0.0
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
