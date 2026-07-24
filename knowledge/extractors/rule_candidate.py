# knowledge/extractors/rule_candidate.py
"""Rule Candidate model."""

from .knowledge_candidate import KnowledgeCandidate

class RuleCandidate(KnowledgeCandidate):
    """Represents an extracted Config Rule or Security Hub control."""
    rule_id: str
    rule_name: str
