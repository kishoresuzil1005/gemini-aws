"""
Universal Scoring Engine.
Calculates risk, confidence, and priority mathematically without cloud-specific knowledge.
"""
from app.services.ai.analyzers.engines.scoring.scoring_models import RiskScore, ConfidenceScore, PriorityScore, ImpactScore
from app.services.ai.analyzers.base.analyzer_models import RiskLevel, Confidence, RecommendationPriority

class ScoringEngine:
    
    @classmethod
    def version(cls) -> str:
        return "1.0.0"

    @staticmethod
    def calculate_risk(blast_radius: int, is_spof: bool, is_isolated: bool) -> RiskScore:
        """
        Calculates mathematical risk purely from generic topology metrics.
        """
        score = 0.0
        reason = "Normal infrastructure."
        level = RiskLevel.LOW
        
        if is_isolated:
            return RiskScore(level=RiskLevel.LOW, numeric_score=0.0, reason="Isolated component poses no architectural risk.")
            
        if is_spof:
            score += 60.0
            reason = "Component is a Single Point of Failure."
            level = RiskLevel.HIGH
            
        if blast_radius > 10:
            score += 30.0
            reason += " Large downstream blast radius."
            level = RiskLevel.CRITICAL if is_spof else RiskLevel.HIGH
        elif blast_radius > 0:
            score += 10.0
            
        if score <= 10.0 and not is_spof:
            level = RiskLevel.LOW
        elif score <= 30.0:
            level = RiskLevel.MEDIUM
            
        return RiskScore(level=level, numeric_score=min(100.0, score), reason=reason.strip())

    @staticmethod
    def calculate_priority(risk: RiskScore) -> PriorityScore:
        if risk.level == RiskLevel.CRITICAL:
            return PriorityScore(level=RecommendationPriority.IMMEDIATE, weight=10, reason="Critical risk requires immediate action.")
        elif risk.level == RiskLevel.HIGH:
            return PriorityScore(level=RecommendationPriority.SHORT_TERM, weight=7, reason="High risk should be addressed soon.")
        return PriorityScore(level=RecommendationPriority.OPTIONAL, weight=3, reason="Low/Medium risk is optional.")
