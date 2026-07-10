from typing import List, Dict, Any
from .mission_manager import MissionManager
from ..models.mission_models import MissionPriority

class MissionScheduler:
    """
    Determines execution priority and ordering for pending missions.
    """
    def __init__(self, manager: MissionManager):
        self.manager = manager

    def get_next_mission(self) -> str:
        """
        Returns the mission_id of the highest priority pending mission.
        """
        active = self.manager.list_active_missions()
        pending = [m for m in active if m.status == "PENDING"]
        if not pending:
            return None
            
        # Priority mapping
        priority_map = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        pending.sort(key=lambda x: priority_map.get(x.priority.value, 0), reverse=True)
        return pending[0].mission_id
