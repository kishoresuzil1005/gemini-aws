from typing import List, Dict, Any

class ConfidenceEngine:
    def __init__(self):
        pass

    def calculate(self, evidence: List[str], tools_used: List[str], llm_raw_response: str) -> int:
        """
        Calculates a confidence score between 0 and 100 based on available evidence
        and tools used.
        """
        base_score = 50
        
        # Add points for evidence
        if evidence:
            base_score += min(len(evidence) * 10, 30)
            
        # Add points for tools
        if tools_used:
            base_score += min(len(tools_used) * 10, 20)
            
        # Cap at 100
        return min(base_score, 100)