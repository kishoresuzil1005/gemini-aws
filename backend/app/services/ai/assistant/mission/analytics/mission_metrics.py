from typing import Dict, Any
from ..memory.mission_history import MissionHistory
from ..models.mission_models import MissionStatus

class MissionMetrics:
    """
    Calculates aggregated statistics across all historical missions.
    """
    def __init__(self, history: MissionHistory):
        self.history = history

    def calculate_metrics(self) -> Dict[str, Any]:
        results = self.history.get_all_results()
        if not results:
            return {"total_missions": 0}
            
        total = len(results)
        successes = sum(1 for r in results if r.status == MissionStatus.COMPLETED)
        avg_duration = sum(r.duration_seconds for r in results) / total
        
        return {
            "total_missions": total,
            "success_rate_pct": (successes / total) * 100.0,
            "average_duration_sec": avg_duration
        }
