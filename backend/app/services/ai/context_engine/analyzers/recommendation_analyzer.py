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
from ..models import AIContext, AnalyzerResult


class RecommendationAnalyzer(BaseAnalyzer):
    """Aggregates all analyzer findings into ranked recommendations."""

    name = "recommendation"

    def analyze(self, context: AIContext) -> AnalyzerResult:
        """Aggregate findings already produced by the analysis lifecycle."""
        all_recommendations = []
        for analyzer_name, result in context.findings.items():
            for finding in result.get("findings", []):
                all_recommendations.append({
                    "id": f"{analyzer_name}-{len(all_recommendations)}",
                    "severity": finding.get("severity", "LOW"),
                    "category": analyzer_name,
                    "title": finding.get("title", ""),
                    "description": finding.get("description", ""),
                    "source": analyzer_name,
                })
                    
        return AnalyzerResult(
            status="success",
            analyzer=self.name,
            findings=all_recommendations,
            recommendations=all_recommendations,
            metadata={
                "count": len(all_recommendations)
            },
        )

    def generate(self, context: AIContext) -> List[Dict[str, Any]]:
        """Return a ranked list of recommendations.

        This is the preferred call‑site method for downstream consumers.
        """
        result = self.analyze(context)
        return result.recommendations or []
