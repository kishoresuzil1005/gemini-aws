# knowledge/normalization/normalization_report.py
"""Reporting models for the Normalization Engine."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class NormalizationReport(BaseModel):
    """Summarizes the outcome of a normalization run."""
    normalization_id: str
    provider: str
    source: str
    document_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    duration_ms: int = 0
    entities_normalized: int = 0
    duplicates_removed: int = 0
    relationships_resolved: int = 0
    quality_score: float = 0.0
    model_counts: Dict[str, int] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
