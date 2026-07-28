# knowledge/extractors/knowledge_candidate.py
"""Base Knowledge Candidate model."""

from typing import Dict, Any
from pydantic import BaseModel

class KnowledgeCandidate(BaseModel):
    """Base model for all extracted knowledge candidates.
    
    Candidates preserve the original raw data, confidence score, and source context.
    """
    candidate_id: str
    provider: str
    source: str
    version: str
    confidence: float
    raw_data: Dict[str, Any]
    metadata: Dict[str, Any] = {}
