from typing import Dict, Any
from app.services.graph.analysis.security.orchestrator import SecurityImpactAnalyzer
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer
from app.services.graph.analysis.blast_radius import BlastRadiusAnalyzer
from app.services.graph.analysis.root_cause import RootCauseAnalyzer
from app.services.ai.recommendation_engine import AIRecommendationEngine
from app.services.ai.remediation_planner import RemediationPlanner
from app.services.ai.orchestrator.remediation_orchestrator import RemediationOrchestrator

class ToolRouter:
    def __init__(self):
        self.security_analyzer = SecurityImpactAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.blast_analyzer = BlastRadiusAnalyzer()
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.recommendation_engine = AIRecommendationEngine()
        self.remediation_planner = RemediationPlanner()
        self.orchestrator = RemediationOrchestrator()

    def route(self, intent: str, resource_id: str) -> Dict[str, Any]:
        """
        Routes the classified intent to the appropriate backend tool.
        """
        if not resource_id:
            return {"error": "No specific resource identified in the query."}
            
        result = {}
        try:
            if intent == "SECURITY_ANALYSIS":
                result["security"] = self.security_analyzer.analyze(resource_id)
                result["recommendations"] = [r.dict() for r in self.recommendation_engine.analyze_resource(resource_id)]
            elif intent == "ROOT_CAUSE":
                result["root_cause"] = self.root_cause_analyzer.analyze(resource_id)
                result["security"] = self.security_analyzer.analyze(resource_id)
                result["recommendations"] = [r.dict() for r in self.recommendation_engine.analyze_resource(resource_id)]
            elif intent == "DEPENDENCY_ANALYSIS":
                result["dependencies"] = self.dependency_analyzer.analyze(resource_id)
            elif intent == "BLAST_RADIUS":
                result["blast_radius"] = self.blast_analyzer.analyze(resource_id)
            elif intent == "REMEDIATION":
                result["remediation"] = [p.dict() for p in self.remediation_planner.plan_for_resource(resource_id)]
            elif intent == "ORCHESTRATION":
                result["orchestration"] = [p.dict() for p in self.orchestrator.build_package(resource_id)]
            else:
                # Default context pull
                result["recommendations"] = [r.dict() for r in self.recommendation_engine.analyze_resource(resource_id)]
        except Exception as e:
            result["error"] = str(e)
            
        return result
