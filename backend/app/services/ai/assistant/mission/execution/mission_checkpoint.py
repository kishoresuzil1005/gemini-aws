from typing import Dict, Any, List
from ..models.mission_models import MissionCheckpoint

class MissionCheckpointManager:
    """
    Records milestones to ensure a mission can resume exactly where it left off
    in case of a system crash or intentional pause.
    """
    def __init__(self):
        self._checkpoints: Dict[str, List[MissionCheckpoint]] = {}

    def save_checkpoint(self, checkpoint: MissionCheckpoint):
        if checkpoint.mission_id not in self._checkpoints:
            self._checkpoints[checkpoint.mission_id] = []
        self._checkpoints[checkpoint.mission_id].append(checkpoint)

    def get_latest_checkpoint(self, mission_id: str) -> MissionCheckpoint:
        history = self._checkpoints.get(mission_id, [])
        return history[-1] if history else Non