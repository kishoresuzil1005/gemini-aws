"""
Recommendation Engine.
Generates structured deterministic recommendations based on dependency findings.
"""
from typing import List
from app.services.ai.analyzers.base.analyzer_models import AnalyzerRecommendation
from app.services.ai.analyzers.engines.dependency.dependency_models import DependencyAnalysis

class RecommendationEngine:
    
    @classmethod
    def generate(cls, analysis: DependencyAnalysis) -> List[AnalyzerRecommendation]:
        """
        Deterministically evaluates findings and produces enterprise recommendations.
        """
        recommendations = []
        
        if analysis.is_spof:
            recommendations.append(AnalyzerRecommendation(
                id=f"REC-SPOF-{analysis.node_id}",
                title="Eliminate Single Point of Failure",
                description=f"Deploy additional instances of {analysis.node_type} in multiple Availability Zones.",
                priority="SHORT_TERM",
                effort="Medium",
                action_type="Architecture Change",
                automation_possible=True,
                estimated_savings=None
            ))
            
        if analysis.cycles:
            recommendations.append(AnalyzerRecommendation(
                id=f"REC-CYCLE-{analysis.node_id}",
                title="Break Circular Dependency",
                description="Refactor architecture to decouple services and eliminate cyclic references.",
                priority="IMMEDIATE",
                effort="High",
                action_type="Refactor",
                automation_possible=False,
                estimated_savings=None
            ))
            
        if analysis.blast_radius > 50:
            recommendations.append(AnalyzerRecommendation(
                id=f"REC-BLAST-{analysis.node_id}",
                title="Reduce Blast Radius",
                description="Implement circuit breakers and decouple downstream dependencies to reduce massive impact.",
                priority="LONG_TERM",
                effort="High",
                action_type="Architecture Change",
                automation_possible=False,
                estimated_savings=None
            ))
            
        return recommendations
