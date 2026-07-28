# knowledge/extractors/operation_candidate.py
"""Operation Candidate model."""

from .knowledge_candidate import KnowledgeCandidate

class OperationCandidate(KnowledgeCandidate):
    """Represents a discovered API action or operation."""
    service_name: str
    operation_name: str
