from .mission_checkpoint import MissionCheckpointManager
from ..core.mission_manager import MissionManager
from ..models.mission_models import MissionStatus

class MissionRecoveryManager:
    """
    Handles automatic recovery and resumption of missions that failed or crashed mid-flight.
    """
    def __init__(self, manager: MissionManager, checkpoint_manager: MissionCheckpointManager):
        self.manager = manager
        self.checkpoint_manager = checkpoint_manager

    def attempt_recovery(self, mission_id: str) -> bool:
        mission = self.manager.get_mission(mission_id)
        if not mission or mission.status != MissionStatus.FAILED:
            return False

        latest_checkpoint = self.checkpoint_manager.get_latest_checkpoint(mission_id)
        if latest_checkpoint:
            print(f"[MissionRecovery] Recovering mission {mission_id} from objective {latest_checkpoint.objective_id}")
            self.manager.update_status(mission_id, MissionStatus.RUNNING)
            return True
            
        return False
