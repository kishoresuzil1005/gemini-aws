"""Single service boundary for graph-backed security analysis."""

from typing import Any, Dict

from app.services.graph.analysis.security.orchestrator import SecurityImpactAnalyzer


class SecurityService:
    """Normalizes access to the existing graph security providers."""

    def __init__(self, knowledge_client: Any = None) -> None:
        self._analyzer = SecurityImpactAnalyzer(knowledge_client)

    def analyze(self, resource_id: str) -> Dict[str, Any]:
        return self._analyzer.analyze(resource_id)
