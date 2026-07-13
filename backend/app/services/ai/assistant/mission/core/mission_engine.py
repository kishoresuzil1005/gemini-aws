from typing import Dict, Any, Optional
from ..models.mission_models import Mission, MissionStatus
from .mission_manager import MissionManager
from ..planning.goal_engine import GoalEngine
from ..execution.mission_executor import MissionExecutor
from ..monitoring.mission_monitor import MissionMonitor

class MissionEngine:
    """
    The top-level orchestrator for Autonomous Mission Control.
    """
    def __init__(self, manager: MissionManager, goal_engine: GoalEngine, executor: MissionExecutor, monitor: MissionMonitor):
        self.manager = manager
        self.goal_engine = goal_engine
        self.executor = executor
        self.monitor = monitor

    def start_mission(self, intent: str, context: Dict[str, Any]) -> str:
        # 1. Plan Goal
        goal = self.goal_engine.formulate_goal(intent)
        # 2. Create Mission
        mission = self.manager.create_mission(intent, goal, context)
        # 3. Execute
        self.executor.execute_async(mission.mission_id)
        return mission.mission_id

    def pause_mission(self, mission_id: str) -> bool:
        return self.manager.update_status(mission_id, MissionStatus.PAUSED)

    def resume_mission(self, mission_id: str) -> bool:
        mission = self.manager.get_mission(mission_id)
        if mission and mission.status == MissionStatus.PAUSED:
            self.manager.update_status(mission_id, MissionStatus.RUNNING)
            self.executor.execute_async(mission_id)
            return True
        return False

    def cancel_mission(self, mission_id: str) -> bool:
        return self.manager.update_status(mission_id, MissionStatus.CANCELLED)

    def get_mission_status(self, mission_id: str) -> Optional[MissionStatus]:
        mission = self.manager.get_mission(mission_id)
        return mission.status if mission else Non