import uuid
from typing import Dict, List, Optional, Any
from ..models.mission_models import Mission, MissionGoal, MissionStatus
from .mission_repository import MissionRepository

class MissionManager:
    """
    Manages the lifecycle and state of missions.
    """
    def __init__(self, repository: MissionRepository):
        self.repository = repository

    def create_mission(self, intent: str, goal: MissionGoal, context: Dict[str, Any] = None) -> Mission:
        mission = Mission(
            mission_id=str(uuid.uuid4()),
            title=f"Mission: {intent[:30]}...",
            intent=intent,
            goal=goal,
            context=context or {}
        )
        self.repository.save(mission)
        return mission

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        return self.repository.get(mission_id)

    def update_status(self, mission_id: str, status: MissionStatus) -> bool:
        mission = self.repository.get(mission_id)
        if mission:
            mission.status = status
            self.repository.save(mission)
            return True
        return False

    def list_active_missions(self) -> List[Mission]:
        all_missions = self.repository.get_all()
        return [m for m in all_missions if m.status in (MissionStatus.PENDING, MissionStatus.RUNNING, MissionStatus.PAUSED)]