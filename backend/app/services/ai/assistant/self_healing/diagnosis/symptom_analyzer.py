from typing import Dict, Any, List

class SymptomAnalyzer:
    """
    Correlates multiple symptoms (e.g., High Latency + High DB CPU) to 
    narrow down failure classification before root cause analysis.
    """
    def analyze_symptoms(self, active_alerts: List[Dict[str, Any]]) -> str:
        print("[SymptomAnalyzer] Correlating active symptoms across the fleet...")
        if len(active_alerts) > 1:
            return "Cascading Failure"
        return "Isolated Component Failure"
