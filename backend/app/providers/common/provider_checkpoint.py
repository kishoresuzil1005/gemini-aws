from typing import Dict, Any

class ProviderCheckpoint:
    """
    Used alongside the Transaction Manager to persist execution states 
    so long-running operations can be resumed.
    """
    def __init__(self):
        self._checkpoints = {}

    def save_checkpoint(self, transaction_id: str, state: Dict[str, Any]):
        self._checkpoints[transaction_id] = state

    def load_checkpoint(self, transaction_id: str) -> Dict[str, Any]:
        return self._checkpoints.get(transaction_id, {})
