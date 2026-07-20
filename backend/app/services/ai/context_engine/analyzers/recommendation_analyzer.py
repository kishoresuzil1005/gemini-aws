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
        """Run all child analyzers and aggregate their findings."""
        from .dependency_analyzer import DependencyAnalyzer
        
        analyzers = [
            DependencyAnalyzer()
        ]
        
        all_recommendations = []
        
        for analyzer in analyzers:
            result = analyzer.analyze(context)
            if result.get("status") == "success":
                findings = result.get("findings", [])
                # Store findings in context natively
                if analyzer.name not in context.findings:
                    context.findings[analyzer.name] = findings
                    
                # Convert findings to recommendations
                for finding in findings:
                    all_recommendations.append({
                        "id": f"{analyzer.name}-{len(all_recommendations)}",
                        "severity": finding.get("severity", "LOW"),
                        "category": analyzer.name,
                        "title": finding.get("title", ""),
                        "description": finding.get("description", ""),
                        "source": analyzer.name,
                    })
                    
        return {
            "status": "success",
            "analyzer": self.name,
            "recommendations": all_recommendations,
            "total": len(all_recommendations),
        }

    def generate(self, context: AIContext) -> List[Dict[str, Any]]:
        """Return a ranked list of recommendations.

        This is the preferred call‑site method for downstream consumers.
        """
        result = self.analyze(context)
        return result.get("recommendations", [])
