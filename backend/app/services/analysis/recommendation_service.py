"""Single entry point for recommendation generation.

This facade preserves the legacy recommendation engines while ensuring API
callers use one authoritative service boundary.
"""

from typing import Any, List, Optional

from app.services.ai.recommendation_engine import AIRecommendationEngine
from app.services.optimization.recommendations import RecommendationEngine as FinOpsRecommendationEngine


class RecommendationService:
    """Coordinates AI and FinOps recommendations without changing API models."""

    def generate_ai(
        self, resource_id: Optional[str] = None, category: Optional[str] = None
    ) -> List[Any]:
        engine = AIRecommendationEngine()
        recommendations = (
            engine.analyze_resource(resource_id)
            if resource_id
            else engine.analyze_environment()
        )
        if category:
            category = category.upper()
            recommendations = [
                item for item in recommendations
                if getattr(item, "category", "").upper() == category
            ]
        return recommendations

    def generate_finops(self, db: Any) -> List[Any]:
        return FinOpsRecommendationEngine.generate(db)
