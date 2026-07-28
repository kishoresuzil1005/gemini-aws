import logging
from knowledge.service.client_factory import get_default_client
from app.services.graph.analysis.architecture_review import ArchitectureReviewer
from app.services.analysis.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)

class AIGraphAgent:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()
        self.architecture_reviewer = ArchitectureReviewer(self.client)

    def generate_recommendations(self):
        """
        Gathers graph data (architecture warnings, isolated nodes, etc.)
        and feeds it to an LLM to generate plain-text recommendations.
        """
        # Step 1: Gather Context
        arch_data = self.architecture_reviewer.analyze()
        
        recommendations = RecommendationService().generate_ai()
        recommendations = [
            getattr(item, "recommendation_text", getattr(item, "description", str(item)))
            for item in recommendations
        ]
        
        return {
            "status": "success",
            "context_analyzed": arch_data,
            "recommendations": recommendations
        }
