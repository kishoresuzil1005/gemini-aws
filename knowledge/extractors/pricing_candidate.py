# knowledge/extractors/pricing_candidate.py
"""Pricing Candidate model."""

from .knowledge_candidate import KnowledgeCandidate

class PricingCandidate(KnowledgeCandidate):
    """Represents an extracted pricing attribute or SKU."""
    service_code: str
    sku: str
