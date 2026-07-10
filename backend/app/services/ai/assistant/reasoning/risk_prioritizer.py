import uuid
from typing import List
from app.services.ai.assistant.reasoning.reasoning_models import Finding, Risk
from app.services.ai.assistant.reasoning.reasoning_rules import ReasoningRules

class RiskPrioritizer:
    def prioritize(self, findings: List[Finding]) -> List[Risk]:
        """
        Identifies risks from findings and sorts them dynamically based on configured rules.
        """
        risks: List[Risk] = []
        
        for finding in findings:
            # Stub: Inspect finding data to identify severity and exposure
            # In reality, this would parse `finding.raw_data` for specific security keys
            is_security = "SecurityTool" in finding.source_tool
            
            if is_security:
                severity = "HIGH" # Extracted from raw_data
                exposure = "PUBLIC" # Extracted from raw_data
                
                base_score = ReasoningRules.get_severity_weight(severity)
                multiplier = ReasoningRules.get_exposure_multiplier(exposure)
                final_score = int(base_score * multiplier)
                
                risk = Risk(
                    id=str(uuid.uuid4()),
                    finding_id=finding.id,
                    severity=severity,
                    description=f"Risk derived from {finding.source_tool}",
                    score=final_score
                )
                risks.append(risk)
                
        # Sort descending by risk score
        risks.sort(key=lambda r: r.score, reverse=True)
        return risks
