from typing import Dict, Any

class GraphCheckpoint:
    """
    Persists state before large sync operations to allow recovery.
    """
    def __init__(self):
        self._checkpoints = {}

    def create_checkpoint(self, checkpoint_id: str, state_data: Dict[str, Any]):
        self._checkpoints[checkpoint_id] = state_data

    def restore_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        return self._checkpoints.get(checkpoint_id, {})