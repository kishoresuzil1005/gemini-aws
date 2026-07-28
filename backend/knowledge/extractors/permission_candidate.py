# knowledge/extractors/permission_candidate.py
"""Permission Candidate model."""

from .knowledge_candidate import KnowledgeCandidate

class PermissionCandidate(KnowledgeCandidate):
    """Represents an extracted IAM permission or policy rule."""
    action: str
    resource_pattern: str
