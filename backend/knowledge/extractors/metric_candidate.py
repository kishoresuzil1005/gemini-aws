# knowledge/extractors/metric_candidate.py
"""Metric Candidate model."""

from .knowledge_candidate import KnowledgeCandidate

class MetricCandidate(KnowledgeCandidate):
    """Represents a discovered CloudWatch Metric."""
    namespace: str
    metric_name: str
