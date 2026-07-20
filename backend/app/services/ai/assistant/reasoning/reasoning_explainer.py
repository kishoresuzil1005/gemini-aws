from typing import List
from app.services.ai.assistant.reasoning.reasoning_models import Finding, Evidence, Risk, Conflict

class ReasoningExplainer:
    def explain(self, findings: List[Finding], evidence: List[Evidence], risks: List[Risk], conflicts: List[Conflict]) -> str:
        """
        Generates a machine-readable or structured explanation of the reasoning process,
        linking Findings -> Evidence -> Risks.
        """
        explanation = "Reasoning Process Summary:\n"
        
        if not findings:
            return explanation + "No findings to explain."
            
        explanation += f"1. Extracted {len(findings)} core findings.\n"
        explanation += f"2. Ranked top {len(evidence)} pieces of evidence.\n"
        
        if conflicts:
            explanation += f"3. Resolved {len(conflicts)} conflicts.\n"
            
        if risks:
            top_risk = risks[0]
            explanation += f"4. Prioritized highest risk: {top_risk.severity} ({top_risk.score}).\n"
            
        return explanation