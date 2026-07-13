from typing import Any

class OperationTracker:
    """Tracks Long Running Operations (LRO)."""
    def __init__(self):
        self.operations = {}

    def track(self, operation_id: str, status: str):
        self.operations[operation_id] = status

    def get_status(self, operation_id: str) -> str:
        return self.operations.get(operation_id, "UNKNOWN")
