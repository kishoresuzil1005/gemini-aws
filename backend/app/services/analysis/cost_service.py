"""Single service boundary for cost analysis.

Collection remains the responsibility of Cost Explorer jobs.  This service
only reads persisted or graph-derived data and exposes compatibility methods.
"""

from typing import Any, Dict

from app.services.graph.analysis.cost import CostAnalyzer


class CostService:
    """Coordinates existing cost analysis without duplicating collectors."""

    def __init__(self, knowledge_client: Any = None) -> None:
        self._analyzer = CostAnalyzer(knowledge_client)

    def analyze_resource(self, resource_id: str) -> Dict[str, Any]:
        return self._analyzer.analyze(resource_id)
