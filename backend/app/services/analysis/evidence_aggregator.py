"""Aggregate authoritative infrastructure evidence for the AI chat pipeline."""

from typing import Any, Dict, List

from app.services.ai.context_engine.models import AIContext, AnalyzerResult
from app.services.analysis.cost_service import CostService
from app.services.analysis.recommendation_service import RecommendationService
from app.services.analysis.security_service import SecurityService
from app.services.graph.analysis.root_cause import RootCauseAnalyzer


class EvidenceAggregator:
    """Enrich the canonical ``AIContext`` without allowing providers to prompt the LLM."""

    def aggregate(self, context: AIContext, resource_id: str | None) -> AIContext:
        evidence: Dict[str, Any] = {
            "infrastructure": context.inventory or context.resource,
            "metrics": context.metrics,
            "dependencies": context.graph or context.relationships,
            "security": context.security,
            "cost": context.cost,
            "recommendations": context.recommendations,
            "findings": context.findings,
            "confidence": self._confidence(context),
            "availability": self._availability(context),
        }

        if resource_id:
            self._append_service_evidence(evidence, context, resource_id)

        context.evidence = evidence
        return context

    @staticmethod
    def _confidence(context: AIContext) -> float:
        executed = len(context.execution.providers_executed)
        failed = len(context.execution.providers_failed)
        total = executed + failed
        return round(executed / total, 2) if total else 0.0

    @staticmethod
    def _availability(context: AIContext) -> Dict[str, str]:
        return {
            "metrics": "available" if context.metrics else "unavailable",
            "cost": "available" if context.cost else "unavailable",
            "security": "available" if context.security else "unavailable",
            "graph": "available" if context.graph else "unavailable",
        }

    def _append_service_evidence(
        self, evidence: Dict[str, Any], context: AIContext, resource_id: str
    ) -> None:
        service_calls = (
            ("security", lambda: SecurityService().analyze(resource_id)),
            ("cost", lambda: CostService().analyze_resource(resource_id)),
            ("root_cause", lambda: RootCauseAnalyzer().analyze(resource_id)),
            ("recommendations", lambda: RecommendationService().generate_ai(resource_id)),
        )
        for name, call in service_calls:
            try:
                value = call()
            except Exception as error:  # An unavailable provider is evidence, not a fabricated result.
                evidence[name] = {"status": "unavailable", "reason": str(error)}
                continue

            serialized = self._serialize(value)
            evidence[name] = serialized
            if name == "root_cause":
                context.findings[name] = AnalyzerResult(
                    analyzer=name,
                    status="success",
                    findings=[serialized],
                    confidence=float(serialized.get("confidence", 0.0)),
                )
            elif name == "recommendations" and isinstance(serialized, list):
                context.recommendations = serialized

    @staticmethod
    def _serialize(value: Any) -> Any:
        if isinstance(value, list):
            return [EvidenceAggregator._serialize(item) for item in value]
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if isinstance(value, dict):
            return {key: EvidenceAggregator._serialize(item) for key, item in value.items()}
        return value
