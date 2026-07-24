"""
Prioritization Engine.
Calculates deterministic ranking scores to prioritize incident remediation and recommendations.
"""
from typing import Dict, Any
from .dependency_models import DependencyAnalysis

class PrioritizationEngine:
    
    @classmethod
    def calculate_priority_score(cls, analysis: DependencyAnalysis, impact: Dict[str, Any]) -> int:
        """
        Combines Risk, Criticality, Blast Radius, Confidence, and Business Impact into a unified score (0-1000).
        """
        score = 0
        
        # Base Risk & Blast Radius
        score += min(analysis.risk_score * 3, 300)
        score += min(analysis.blast_radius * 2, 200)
        
        # Business Criticality weights
        criticality_weights = {
            "Mission Critical": 300,
            "Production": 200,
            "Customer Facing": 150,
            "Shared Platform": 100,
            "Internal": 50,
            "Development": 20,
            "Sandbox": 0
        }
        score += criticality_weights.get(analysis.business_criticality, 0)
        
        # Incident Impact weights
        impact_weights = {
            "Critical": 150,
            "High": 100,
            "Medium": 50,
            "Low": 10,
            "None": 0
        }
        score += impact_weights.get(impact.get("business_impact", "Low"), 0)
        
        # SPOF multiplier
        if analysis.is_spof:
            score += 50
            
        return min(score, 1000)
