from typing import Optional, Dict, Any, List
from app.services.ai.assistant.graph_assistant import GraphAssistant
from app.services.ai.recommendation_engine import AIRecommendationEngine
from app.services.ai.remediation_planner import RemediationPlanner
from app.services.ai.orchestrator.remediation_orchestrator import RemediationOrchestrator

class AIEngine:
    """
    The unified AI Engine that orchestrates all AI capabilities.
    Acts as a facade over Chat, Recommendations, and Actions.
    """
    
    def __init__(self, memory_manager=None):
        self.memory = memory_manager
        
    def chat(self, request, stream: bool = False):
        assistant = GraphAssistant(self.memory)
        return assistant.chat(request, stream=stream)
        
    def recommend(self, resource_id: Optional[str] = None, category: Optional[str] = None) -> List[Any]:
        engine = AIRecommendationEngine()
        if resource_id:
            return engine.analyze_resource(resource_id)
        
        recs = engine.analyze_environment()
        if category:
            recs = [r for r in recs if r.category == category.upper()]
        return recs

    def plan_remediation(self, resource_id: Optional[str] = None) -> List[Any]:
        planner = RemediationPlanner()
        if resource_id:
            return planner.plan_for_resource(resource_id)
        return planner.plan_environment()

    def build_orchestration(self, resource_id: Optional[str] = None) -> List[Any]:
        orchestrator = RemediationOrchestrator()
        if resource_id:
            return orchestrator.build_package(resource_id)
        return orchestrator.build_environment_packages()

    def get_tools(self) -> List[Dict]:
        assistant = GraphAssistant(self.memory)
        return assistant.tool_router.registry.list_tools(