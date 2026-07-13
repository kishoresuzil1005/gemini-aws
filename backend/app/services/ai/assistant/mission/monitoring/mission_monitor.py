from typing import Dict, Any
from ..core.mission_manager import MissionManager

class MissionMonitor:
    """
    Monitors the ongoing status, health, and warnings of active missions.
    """
    def __init__(self, manager: MissionManager):
        self.manager = manager

    def get_mission_health(self, mission_id: str) -> Dict[str, Any]:
        mission = self.manager.get_mission(mission_id)
        if not mission:
            return {"status": "NOT_FOUND"}
            
        return {
            "mission_id": mission_id,
            "status": mission.status.value,
            "is_healthy": mission.status not in ["FAILED", "CANCELLED"]
        }