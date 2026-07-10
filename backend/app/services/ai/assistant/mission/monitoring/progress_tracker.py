from typing import Dict, Any
from ..core.mission_manager import MissionManager
from ..models.mission_models import MissionStatus

class ProgressTracker:
    """
    Calculates completion percentages based on the total number of objectives vs completed ones.
    """
    def __init__(self, manager: MissionManager):
        self.manager = manager

    def get_progress(self, mission_id: str) -> Dict[str, Any]:
        mission = self.manager.get_mission(mission_id)
        if not mission or not mission.goal.objectives:
            return {"percentage": 0.0, "completed": 0, "total": 0}
            
        total = len(mission.goal.objectives)
        completed = sum(1 for obj in mission.goal.objectives if obj.status == MissionStatus.COMPLETED)
        
        return {
            "percentage": (completed / total) * 100.0,
            "completed": completed,
            "total": total
        }
