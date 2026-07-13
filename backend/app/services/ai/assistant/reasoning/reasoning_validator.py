from typing import List
from app.services.ai.assistant.reasoning.reasoning_models import Finding, Evidence, Risk, Conflict

class ReasoningValidator:
    def validate(self, findings: List[Finding], evidence: List[Evidence], risks: List[Risk], conflicts: List[Conflict]) -> tuple[bool, List[str]]:
        """
        Verifies reasoning quality. Checks for missing evidence, empty reasoning, etc.
        """
        errors = []
        is_valid = True
        
        if not findings:
            errors.append("No findings extracted from tool results.")
            is_valid = False
            
        if not evidence:
            errors.append("No supporting evidence found.")
            is_valid = False
            
        # Check for unresolved conflicts
        for conflict in conflicts:
            if not conflict.resolved:
                errors.append(f"Unresolved conflict detected: {conflict.id}")
                is_valid = False
                
        # Check references (all evidence should point to a valid finding)
        finding_ids = {f.id for f in findings}
        for e in evidence:
            if e.finding_id not in finding_ids:
                errors.append(f"Broken reference: Evidence {e.id} points to missing finding {e.finding_id}")
                is_valid = False
                
        return is_valid, error