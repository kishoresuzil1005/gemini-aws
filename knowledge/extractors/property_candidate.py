# knowledge/extractors/property_candidate.py
"""Property Candidate model."""

from .knowledge_candidate import KnowledgeCandidate

class PropertyCandidate(KnowledgeCandidate):
    """Represents a discovered property or attribute of a resource."""
    resource_type: str
    property_name: str
    property_type: str
