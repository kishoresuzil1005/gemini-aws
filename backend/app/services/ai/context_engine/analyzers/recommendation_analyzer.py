"""RecommendationAnalyzer – aggregates findings from all analyzers into ranked recommendations.

This is the final deterministic step before the Prompt Builder.

Architecture
------------
::

    ArchitectureAnalyzer ─┐
    SecurityAnalyzer     ─┤
    CostAnalyzer         ─┤
    PerformanceAnalyzer  ─┼──→ RecommendationAnalyzer ──→ Prompt Builder ──→ LLM
    MigrationAnalyzer    ─┤
    ReliabilityAnalyzer  ─┤
    ComplianceAnalyzer   ─┘

The LLM explains and contextualizes recommendations – it does not invent them.

Status: ``stub``

Replace :meth:`generate` with real aggregation logic in Phase 3.

Planned output shape::

    [
        {
            "id":           str,       # unique recommendation ID
            "severity":     str,       # "critical" | "high" | "medium" | "low"
            "category":     str,       # "security" | "cost" | "reliability" ...
            "title":        str,
            "description":  str,
            "remediation":  str,
            "source":       str,       # analyzer that produced the finding
            "resource_id":  str,
        }
    ]
"""

from typing import Any, Dict, List

from .base_analyzer import BaseAnalyzer
from ..models import AIContext


class RecommendationAnalyzer(BaseAnalyzer):
    """Aggregates all analyzer findings into ranked recommendations."""

    name = "recommendation"

    def analyze(self, context: AIContext) -> Dict[str, Any]:
        """Run all child analyzers and aggregate their findings.

        TODO: Implement in Phase 3 – wire up each analyzer and merge findings.
        """
        return {
            "status":          "not_implemented",
            "analyzer":        self.name,
            "recommendations": [],
            "total":           0,
        }

    def generate(self, context: AIContext) -> List[Dict[str, Any]]:
        """Return a ranked list of recommendations.

        This is the preferred call‑site method for downstream consumers.
        """
        result = self.analyze(context)
        return result.get("recommendations", [])
