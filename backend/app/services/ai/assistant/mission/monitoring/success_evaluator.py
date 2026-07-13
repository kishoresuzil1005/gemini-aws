from typing import Dict, Any
from ..models.mission_models import Mission, MissionResult, MissionStatus

class SuccessEvaluator:
    """
    Determines if a mission truly succeeded by measuring the outcome against the original goal metrics.
    """
    def evaluate(self, mission: Mission, execution_metrics: Dict[str, Any]) -> MissionResult:
        # Example: if goal was 20% reduction, check if we hit it
        target = mission.goal.metrics.get("target_reduction_pct", 0)
        actual = execution_metrics.get("actual_reduction_pct", 0)
        
        status = MissionStatus.COMPLETED if actual >= target else MissionStatus.FAILED
        
        return MissionResult(
            mission_id=mission.mission_id,
            status=status,
            duration_seconds=execution_metrics.get("duration", 0),
            metrics_achieved={"actual_reduction_pct": actual},
            insights=["Target met successfully"] if status == MissionStatus.COMPLETED else ["Fell short of target"]
        