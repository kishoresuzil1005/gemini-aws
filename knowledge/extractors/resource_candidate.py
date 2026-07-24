# knowledge/extractors/resource_candidate.py
"""Resource Candidate model."""

from .knowledge_candidate import KnowledgeCandidate

class ResourceCandidate(KnowledgeCandidate):
    """Represents an extracted cloud resource (e.g., AWS::EC2::Instance)."""
    resource_type: str
    resource_name: str
