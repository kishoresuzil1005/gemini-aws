# knowledge/extractors/relationship_candidate.py
"""Relationship Candidate model."""

from .knowledge_candidate import KnowledgeCandidate

class RelationshipCandidate(KnowledgeCandidate):
    """Represents a discovered relationship (e.g., EC2 -> VPC)."""
    source_entity: str
    target_entity: str
    relationship_type: str
